"""原液×工程ルート(crude_product_process_routes) Excel取込サービス。

入力: docs/reference/第38期原価計算v8(最終))_260225.xlsb のような原価計算 xlsb。
読込シート: '2.1④' (原液→原液変換の記録)
  - A列: 受入原液コード (例: '1-19-2A')
  - B列: 受入原液名     (例: '19HIA')
  - C列: 使用原液コード
  - D列: 使用原液名
  - E列: 使用原液量
  - F列: Q_受入記録.工程名
  - G列: Q_使用記録.工程名 (こちらを採用)

ロジック:
  1. xlsb を pyxlsb でパース
  2. (受入原液コード, 工程名) ごとに使用原液量を合計
  3. crude_products.code でマッチ・processes.name でマッチ
  4. crude_product_process_routes に upsert (UNIQUE: crude×process×period)
"""

import io
import os
import tempfile
import uuid
from datetime import datetime
from decimal import Decimal

from pyxlsb import open_workbook
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.audit import ImportBatch, ImportError as ImportErrorModel, ImportStatus
from app.models.cost import SourceSystem
from app.models.master import (
    CrudeProduct,
    CrudeProductProcessRoute,
    FiscalPeriod,
    Process,
)


SHEET_ROUTES = "2.1④"


def _to_decimal(v) -> Decimal:
    if v is None:
        return Decimal("0")
    s = str(v).strip()
    if not s or s in ("ー", "−", "-"):
        return Decimal("0")
    try:
        return Decimal(s)
    except Exception:
        return Decimal("0")


def parse_route_rows(file_content: bytes, sheet_name: str = SHEET_ROUTES) -> list[dict]:
    """xlsb から (受入原液コード, 受入原液名, 工程名, 使用原液量) を抽出して集計。

    同一の (crude_code, process_name) ペアは合計する。
    """
    aggregated: dict[tuple[str, str], dict] = {}

    with tempfile.NamedTemporaryFile(delete=False, suffix=".xlsb") as tmp:
        tmp.write(file_content)
        path = tmp.name
    try:
        with open_workbook(path) as wb:
            with wb.get_sheet(sheet_name) as sh:
                rows = list(sh.rows())
                if not rows:
                    return []
                header = [c.v for c in rows[0]]
                # column indexes
                try:
                    code_idx = header.index("受入原液コード")
                    name_idx = header.index("受入原液名")
                except ValueError as e:
                    raise ValueError(f"必要なカラムが見つかりません: {e}")
                qty_idx = header.index("使用原液量") if "使用原液量" in header else 4
                # 工程名は使用記録側を優先、受入記録側にフォールバック
                proc_idx = None
                for cand in ("Q_使用記録.工程名", "Q_受入記録.工程名", "工程名"):
                    if cand in header:
                        proc_idx = header.index(cand)
                        break
                if proc_idx is None:
                    raise ValueError("工程名カラムが見つかりません")

                for row in rows[1:]:
                    vals = [c.v for c in row]
                    pad = max(code_idx, name_idx, qty_idx, proc_idx) + 1
                    while len(vals) < pad:
                        vals.append(None)
                    crude_code = vals[code_idx]
                    crude_name = vals[name_idx]
                    process_name = vals[proc_idx]
                    qty = vals[qty_idx]
                    if not isinstance(crude_code, str) or not isinstance(process_name, str):
                        continue
                    crude_code = crude_code.strip()
                    process_name = process_name.strip()
                    if not crude_code or not process_name:
                        continue
                    key = (crude_code, process_name)
                    if key not in aggregated:
                        aggregated[key] = {
                            "crude_code": crude_code,
                            "crude_name": (crude_name.strip() if isinstance(crude_name, str) else ""),
                            "process_name": process_name,
                            "quantity": Decimal("0"),
                        }
                    aggregated[key]["quantity"] += _to_decimal(qty)
    finally:
        os.unlink(path)

    return list(aggregated.values())


async def _resolve_maps(
    db: AsyncSession,
) -> tuple[dict[str, uuid.UUID], dict[str, uuid.UUID]]:
    """code/name → id のマップを作成。"""
    crude_res = await db.execute(select(CrudeProduct))
    crude_map = {cp.code: cp.id for cp in crude_res.scalars().unique().all()}
    proc_res = await db.execute(select(Process))
    proc_map = {p.name: p.id for p in proc_res.scalars().unique().all()}
    return crude_map, proc_map


async def upsert_routes(
    db: AsyncSession,
    period_id: uuid.UUID,
    rows: list[dict],
    crude_map: dict[str, uuid.UUID],
    proc_map: dict[str, uuid.UUID],
) -> dict:
    """ルートテーブルを upsert。集計済み rows を入力に取る。"""
    # 既存ルート
    existing_res = await db.execute(
        select(CrudeProductProcessRoute).where(
            CrudeProductProcessRoute.period_id == period_id
        )
    )
    existing_map: dict[tuple[uuid.UUID, uuid.UUID], CrudeProductProcessRoute] = {
        (r.crude_product_id, r.process_id): r for r in existing_res.scalars().unique().all()
    }

    inserted = 0
    updated = 0
    unchanged = 0
    unmatched_crude: list[str] = []
    unmatched_process: list[str] = []
    for item in rows:
        crude_id = crude_map.get(item["crude_code"])
        process_id = proc_map.get(item["process_name"])
        if crude_id is None:
            unmatched_crude.append(item["crude_code"])
            continue
        if process_id is None:
            unmatched_process.append(item["process_name"])
            continue

        key = (crude_id, process_id)
        existing = existing_map.get(key)
        if existing is None:
            db.add(CrudeProductProcessRoute(
                crude_product_id=crude_id,
                process_id=process_id,
                period_id=period_id,
                actual_quantity=item["quantity"],
            ))
            inserted += 1
        else:
            if Decimal(str(existing.actual_quantity)) != item["quantity"]:
                existing.actual_quantity = item["quantity"]
                updated += 1
            else:
                unchanged += 1
    await db.flush()
    return {
        "inserted": inserted,
        "updated": updated,
        "unchanged": unchanged,
        "unmatched_crude": list(set(unmatched_crude)),
        "unmatched_process": list(set(unmatched_process)),
    }


async def process_crude_process_route_import(
    db: AsyncSession,
    file_content: bytes,
    filename: str,
    period_id: uuid.UUID,
    sheet_name: str = SHEET_ROUTES,
    source_system: str = "manual",
) -> ImportBatch:
    batch = ImportBatch(
        file_name=filename,
        source_system=source_system if source_system in SourceSystem._value2member_map_
        else SourceSystem.manual.value,
        status=ImportStatus.processing,
        period_id=period_id,
        total_rows=0,
        success_rows=0,
        error_rows=0,
        started_at=datetime.now(),
    )
    db.add(batch)
    await db.flush()

    # 期間チェック
    period_res = await db.execute(
        select(FiscalPeriod).where(FiscalPeriod.id == period_id)
    )
    if period_res.scalar_one_or_none() is None:
        batch.status = ImportStatus.failed
        batch.completed_at = datetime.now()
        batch.notes = f"指定された会計期間が見つかりません: {period_id}"
        db.add(ImportErrorModel(batch_id=batch.id, row_number=0, error_message=batch.notes))
        await db.flush()
        await db.refresh(batch)
        return batch

    try:
        rows = parse_route_rows(file_content, sheet_name)
    except Exception as e:
        batch.status = ImportStatus.failed
        batch.completed_at = datetime.now()
        batch.notes = f"ファイルパースエラー: {e}"
        db.add(ImportErrorModel(batch_id=batch.id, row_number=0, error_message=batch.notes))
        await db.flush()
        await db.refresh(batch)
        return batch

    crude_map, proc_map = await _resolve_maps(db)
    batch.total_rows = len(rows)

    stats = await upsert_routes(db, period_id, rows, crude_map, proc_map)
    batch.success_rows = stats["inserted"] + stats["updated"]
    skipped = len(stats["unmatched_crude"]) + len(stats["unmatched_process"])
    batch.error_rows = 0
    batch.status = ImportStatus.completed
    batch.completed_at = datetime.now()
    batch.notes = (
        f"routes: {len(rows)} aggregated rows (INSERT {stats['inserted']} / "
        f"UPDATE {stats['updated']} / UNCHANGED {stats['unchanged']}); "
        f"unmatched crude codes={len(stats['unmatched_crude'])}, "
        f"unmatched processes={len(stats['unmatched_process'])}"
    )
    # 一致しなかったものは ImportError に記録(参考情報)
    for code in stats["unmatched_crude"]:
        db.add(ImportErrorModel(
            batch_id=batch.id, row_number=0,
            error_message=f"unmatched crude_product code: {code}",
        ))
    for pname in stats["unmatched_process"]:
        db.add(ImportErrorModel(
            batch_id=batch.id, row_number=0,
            error_message=f"unmatched process name: {pname}",
        ))
    await db.flush()
    await db.refresh(batch)
    return batch
