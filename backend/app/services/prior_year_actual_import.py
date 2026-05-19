"""前年実績(F-01) インポートサービス —
30SC製品rev1.xlsx 「5.製品」シートから 第38期の製品別 SC 原価フローを
prior_year_actuals テーブルに upsert する。

シート構造 (5.製品):
  R1   タイトル "第38期 製品"
  R3   大項目ヘッダ (商品コード/商品名/期首棚卸/...)
  R4   副項目ヘッダ (数量/単価/原価)
  R5〜 データ行

列マップ (1-origin):
  1: カテゴリ (製造/仕入/製造振替/AB)
  2: 商品コード
  3: 商品名
  4-6:   期首商品棚卸高 (数量/単価/原価)
  7-9:   当期商品製造･仕入原価 (数量/単価/原価)
  10-12: 振替 (数量/単価/原価)
  13-15: 当期商品売上原価 (数量/単価/原価)
  16-18: 外注支給分 (数量/単価/原価)
  19-20: 販売促進費(DM) (数量/原価)
  21-22: 販売促進費 (数量/原価)
  23-24: 試験研究費 (数量/原価)
  25-26: 接待交際費 (数量/原価)
  27-28: 寄付金 (数量/原価)
  29-30: 広告宣伝費 (数量/原価)
  31-32: 在庫調整 (数量/原価)
  33-35: 期末商品棚卸高 (数量/単価/原価)

R1537以降は合計・差異行なのでスキップ。
"""

import io
import uuid
from datetime import datetime
from decimal import Decimal

from openpyxl import load_workbook
from sqlalchemy import delete, select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.audit import ImportBatch, ImportError as ImportErrorModel, ImportStatus
from app.models.cost import PriorYearActual, SourceSystem
from app.models.master import Product


SHEET_PRODUCT = "5.製品"

VALID_CATEGORIES = {"製造", "仕入", "製造振替", "AB"}

# 振替系7項目: (Excel上の項目名, JSON キー, 数量列, 原価列)
TRANSFER_ITEM_COLS: list[tuple[str, str, int, int]] = [
    ("販売促進費(DM)", "promo_dm", 19, 20),
    ("販売促進費", "promo", 21, 22),
    ("試験研究費", "rnd", 23, 24),
    ("接待交際費", "entertainment", 25, 26),
    ("寄付金", "donation", 27, 28),
    ("広告宣伝費", "advertising", 29, 30),
    ("在庫調整", "inventory_adj", 31, 32),
]


def _to_decimal(v) -> Decimal:
    """セル値を Decimal に変換。空/エラー値は 0 とする。"""
    if v is None:
        return Decimal("0")
    if isinstance(v, str):
        s = v.strip()
        if not s or s in ("ー", "−", "-", "#REF!", "#N/A"):
            return Decimal("0")
        try:
            return Decimal(s)
        except Exception:
            return Decimal("0")
    try:
        return Decimal(str(v))
    except Exception:
        return Decimal("0")


def _normalize_code(v) -> str | None:
    """商品コードを文字列化。"""
    if v is None:
        return None
    s = str(v).strip()
    return s if s else None


MAIN_GROUPS = ("opening", "manufacturing", "transfer", "cogs", "outsource_supply", "closing")


def _recompute_unit_prices(r: dict) -> None:
    """合算後の qty/cost から unit_price を再計算する (qty=0 の場合は維持)。"""
    for prefix in MAIN_GROUPS:
        qty = r[f"{prefix}_qty"]
        cost = r[f"{prefix}_cost"]
        if qty and qty != 0:
            r[f"{prefix}_unit_price"] = (cost / qty).quantize(Decimal("0.000001"))


def _merge_row(existing: dict, new: dict) -> None:
    """同コードの2行目以降を 1行目 (existing) に合算する。"""
    for prefix in MAIN_GROUPS:
        existing[f"{prefix}_qty"] += new[f"{prefix}_qty"]
        existing[f"{prefix}_cost"] += new[f"{prefix}_cost"]
    # 振替系 JSONB
    for k, v in new["transfer_items"].items():
        ex_v = existing["transfer_items"].get(k)
        if ex_v is None:
            existing["transfer_items"][k] = v
            continue
        ex_qty = Decimal(ex_v["qty"]) + Decimal(v["qty"])
        ex_cost = Decimal(ex_v["cost"]) + Decimal(v["cost"])
        existing["transfer_items"][k] = {
            "label": ex_v.get("label") or v.get("label"),
            "qty": str(ex_qty),
            "cost": str(ex_cost),
        }
    existing["_merged_count"] = existing.get("_merged_count", 1) + 1


def parse_product_sheet(content: bytes, sheet_name: str = SHEET_PRODUCT) -> list[dict]:
    """5.製品 シートをパースし、商品コード単位で集約した行リストを返す。

    同一 product_code の行 (例: 「(有償支給分)」が別行で存在するケース) は
    qty/cost を合算し、unit_price は合算後の cost/qty で再計算する。
    product_name は最初に出現した行のものを採用 (メイン商品名)。
    """
    wb = load_workbook(io.BytesIO(content), data_only=True, read_only=True)
    ws = wb[sheet_name]
    by_code: dict[str, dict] = {}
    order: list[str] = []
    for ri, row in enumerate(ws.iter_rows(values_only=True), start=1):
        if ri < 5:
            continue
        if len(row) < 35:
            continue
        cat = row[0]
        if cat is None:
            continue
        cat_s = str(cat).strip()
        if cat_s not in VALID_CATEGORIES:
            continue
        code = _normalize_code(row[1])
        if not code:
            continue
        name = row[2]
        name_s = str(name).strip() if name else None

        transfer_items: dict[str, dict[str, str]] = {}
        for label, json_key, qcol, ccol in TRANSFER_ITEM_COLS:
            qty = _to_decimal(row[qcol - 1])
            cost = _to_decimal(row[ccol - 1])
            transfer_items[json_key] = {
                "label": label,
                "qty": str(qty),
                "cost": str(cost),
            }

        parsed = {
            "category": cat_s,
            "product_code": code,
            "product_name": name_s,
            "opening_qty": _to_decimal(row[3]),
            "opening_unit_price": _to_decimal(row[4]),
            "opening_cost": _to_decimal(row[5]),
            "manufacturing_qty": _to_decimal(row[6]),
            "manufacturing_unit_price": _to_decimal(row[7]),
            "manufacturing_cost": _to_decimal(row[8]),
            "transfer_qty": _to_decimal(row[9]),
            "transfer_unit_price": _to_decimal(row[10]),
            "transfer_cost": _to_decimal(row[11]),
            "cogs_qty": _to_decimal(row[12]),
            "cogs_unit_price": _to_decimal(row[13]),
            "cogs_cost": _to_decimal(row[14]),
            "outsource_supply_qty": _to_decimal(row[15]),
            "outsource_supply_unit_price": _to_decimal(row[16]),
            "outsource_supply_cost": _to_decimal(row[17]),
            "closing_qty": _to_decimal(row[32]),
            "closing_unit_price": _to_decimal(row[33]),
            "closing_cost": _to_decimal(row[34]),
            "transfer_items": transfer_items,
        }
        if code in by_code:
            _merge_row(by_code[code], parsed)
        else:
            by_code[code] = parsed
            order.append(code)

    # 合算後の単価を再計算
    for code in order:
        if by_code[code].get("_merged_count"):
            _recompute_unit_prices(by_code[code])

    wb.close()
    return [by_code[c] for c in order]


async def resolve_product_ids(
    db: AsyncSession, codes: set[str]
) -> dict[str, uuid.UUID]:
    """商品コードから product_id を解決。マスタにない場合は除外。"""
    if not codes:
        return {}
    res = await db.execute(
        select(Product.id, Product.code).where(Product.code.in_(codes))
    )
    return {code: pid for pid, code in res.all()}


async def process_prior_year_actual_import(
    db: AsyncSession,
    file_content: bytes,
    filename: str,
    fiscal_year: int,
    sheet_name: str = SHEET_PRODUCT,
    source_system: str = "manual",
    delete_existing: bool = True,
    period_id: uuid.UUID | None = None,
) -> ImportBatch:
    """前年実績 Excel を取り込み、ImportBatch を返す。

    fiscal_year=38 で 30SC製品rev1.xlsx を取り込む想定。
    delete_existing=True (デフォルト) で既存の同 fiscal_year レコードを
    全削除してから登録（マスタ的データなので冪等取込）。
    """
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

    # Excel パース
    try:
        rows = parse_product_sheet(file_content, sheet_name)
    except Exception as e:
        batch.status = ImportStatus.failed
        batch.completed_at = datetime.now()
        batch.notes = f"ファイルパースエラー: {e}"
        db.add(ImportErrorModel(batch_id=batch.id, row_number=0, error_message=batch.notes))
        await db.flush()
        await db.refresh(batch)
        return batch

    batch.total_rows = len(rows)

    if delete_existing:
        await db.execute(
            delete(PriorYearActual).where(PriorYearActual.fiscal_year == fiscal_year)
        )
        await db.flush()

    # 商品コード→product_id マッピング
    codes = {r["product_code"] for r in rows}
    code_to_pid = await resolve_product_ids(db, codes)

    success = 0
    matched = 0
    unmatched = 0
    by_category: dict[str, int] = {}
    cogs_sum = Decimal("0")
    manu_sum = Decimal("0")
    close_sum = Decimal("0")

    for r in rows:
        pid = code_to_pid.get(r["product_code"])
        if pid is not None:
            matched += 1
        else:
            unmatched += 1
        rec = PriorYearActual(
            fiscal_year=fiscal_year,
            category=r["category"],
            product_code=r["product_code"],
            product_name=r["product_name"],
            product_id=pid,
            opening_qty=r["opening_qty"],
            opening_unit_price=r["opening_unit_price"],
            opening_cost=r["opening_cost"],
            manufacturing_qty=r["manufacturing_qty"],
            manufacturing_unit_price=r["manufacturing_unit_price"],
            manufacturing_cost=r["manufacturing_cost"],
            transfer_qty=r["transfer_qty"],
            transfer_unit_price=r["transfer_unit_price"],
            transfer_cost=r["transfer_cost"],
            cogs_qty=r["cogs_qty"],
            cogs_unit_price=r["cogs_unit_price"],
            cogs_cost=r["cogs_cost"],
            outsource_supply_qty=r["outsource_supply_qty"],
            outsource_supply_unit_price=r["outsource_supply_unit_price"],
            outsource_supply_cost=r["outsource_supply_cost"],
            closing_qty=r["closing_qty"],
            closing_unit_price=r["closing_unit_price"],
            closing_cost=r["closing_cost"],
            transfer_items=r["transfer_items"],
            source_file=filename,
            source_sheet=sheet_name,
            import_batch_id=batch.id,
        )
        db.add(rec)
        success += 1
        by_category[r["category"]] = by_category.get(r["category"], 0) + 1
        cogs_sum += r["cogs_cost"]
        manu_sum += r["manufacturing_cost"]
        close_sum += r["closing_cost"]

    await db.flush()

    batch.success_rows = success
    batch.error_rows = 0
    batch.status = ImportStatus.completed
    batch.completed_at = datetime.now()
    cat_summary = ", ".join(f"{k}={v}" for k, v in sorted(by_category.items()))
    batch.notes = (
        f"fiscal_year={fiscal_year}, total={len(rows)}, success={success}, "
        f"matched={matched}, unmatched={unmatched}; categories: {cat_summary}; "
        f"cogs_sum={cogs_sum:.0f}, manufacturing_sum={manu_sum:.0f}, "
        f"closing_sum={close_sum:.0f}"
    )
    await db.flush()
    await db.refresh(batch)
    return batch
