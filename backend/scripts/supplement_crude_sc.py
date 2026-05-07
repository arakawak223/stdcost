"""決算用SC仕掛品.xlsx の「仕掛品SC明細」シートから原液の標準単価を取得し、
CrudeProductStandardCost を補完して在庫評価金額を再計算する。

シート構造 (仕掛品SC明細):
  C列(3): 種類 (例: "13R", "20HI", "44R") — 原液名
  D列(4): 名寄 (例: "R", "HI", "その他") — 単価分類
  E列(5): SC単価 (円/kg) — 標準単価

マッチング戦略:
  1. 直接マッチ: inventory_valuations.item_name == 仕掛品SC明細[C列]
  2. 名寄フォールバック: 一致しない場合、name の crude_type 推定値で名寄単価を採用

使い方:
  cd backend
  python -m scripts.supplement_crude_sc \\
      --period-id 1c533e58-25a8-4e87-9693-e07eb202611a \\
      --sc-xlsx 'docs/reference/決算用SC仕掛品.xlsx'
"""
import argparse
import asyncio
import os
import sys
import uuid
from decimal import Decimal
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

import openpyxl
from sqlalchemy import select, func
from app.db.session import async_session_factory
from app.models.cost import (
    CrudeProductStandardCost, InventoryCategory, InventoryValuation,
)
from app.models.master import CrudeProduct
from app.services.inventory_valuation import recalculate_valuation_amounts

SC_SHEET = '仕掛品SC明細'


def load_sc_maps(xlsx_path: str) -> tuple[dict[str, Decimal], dict[str, Decimal]]:
    """仕掛品SC明細 シートから 2つの辞書を返す:
      name_map: 種類名 (C列) → SC単価
      nayose_map: 名寄カテゴリ (D列) → SC単価 (同名寄内で平均)
    """
    wb = openpyxl.load_workbook(xlsx_path, read_only=True, data_only=True)
    ws = wb[SC_SHEET]

    name_map: dict[str, Decimal] = {}
    nayose_acc: dict[str, list[Decimal]] = {}
    for ri, row in enumerate(ws.iter_rows(values_only=True), start=1):
        if ri < 5:
            continue
        name = row[2] if len(row) > 2 else None
        nayose = row[3] if len(row) > 3 else None
        sc = row[4] if len(row) > 4 else None
        if name is None or sc is None:
            continue
        try:
            price = Decimal(str(sc))
        except Exception:
            continue
        if price <= 0:
            continue
        nm = str(name).strip()
        if nm and nm not in name_map:
            name_map[nm] = price
        if nayose:
            nay = str(nayose).strip()
            nayose_acc.setdefault(nay, []).append(price)

    nayose_map: dict[str, Decimal] = {}
    for k, vs in nayose_acc.items():
        # 同一名寄内ではほぼ同価格(Excel上の前提)。最頻値=最小値ではなく、平均で安全側
        avg = sum(vs) / Decimal(len(vs))
        # 整数四捨五入(原価は円単位)
        nayose_map[k] = avg.quantize(Decimal("1"))

    wb.close()
    return name_map, nayose_map


def infer_nayose_from_name(name: str) -> str | None:
    """name の先頭(数字を除く)から 名寄カテゴリを推定する。
    `仕掛品名寄(貼付)`シート相当のロジックを近似で実装。
    """
    import re
    if not name:
        return None
    n = str(name).strip()
    # 数字 prefix を除去
    m = re.match(r"^\d+(.*)$", n)
    body = m.group(1) if m else n
    # 長いマッチを優先
    candidates = [
        ('HIBkai', 'HIB海'), ('HIB海', 'HIB海'),
        ('HIB', 'HIB'), ('HIA', 'HIA'),
        ('HIR', 'HIR'),
        ('HIpa', 'HIパ'), ('HIﾊﾟ', 'HIパ'), ('HIパ', 'HIパ'),
        ('HI', 'HI'),
        ('PXA', 'PXA'), ('PXM', 'PX'), ('PX', 'PX'),
        ('PE', 'PE'),
        ('PSA', 'PXA'),
        ('GA', 'GA'), ('GB', 'GB'), ('GP', 'GP'),
        ('GIN', 'R'),  # GIN系はR扱い
        ('RB', 'RB'), ('RG', 'RG'), ('RGI', 'RGI'),
        ('Rﾘ', 'Rリ'), ('Rリ', 'Rリ'),
        ('Rﾏ', 'Rマ'), ('Rマ', 'Rマ'),
        ('Rｼ', 'Rシ'), ('Rシ', 'Rシ'),
        ('R3', 'R3'), ('R2', 'R2'), ('R1', 'R1'),
        ('RX', 'RX'),
        ('R', 'R'),
        ('MP', 'MP'),
        ('LPA', 'LPA'), ('LP', 'LP'),
        ('FEB', 'FEB'), ('FB', 'FB'),
        ('BM', 'BM'),
        ('B', 'B'),
        ('植物用', '植物用'),
        ('圧搾', '圧搾カス'),
        ('ろ過', 'その他'),
    ]
    for prefix, nay in candidates:
        if body.startswith(prefix):
            return nay
    # 試作品/研究室用などは その他
    if any(k in body for k in ['試作', '研究', '試験']):
        return 'その他'
    return None


async def run(period_id: uuid.UUID, sc_xlsx: str):
    name_map, nayose_map = load_sc_maps(sc_xlsx)
    print(f"仕掛品SC明細: 種類={len(name_map)}件, 名寄={len(nayose_map)}件")
    print(f"名寄単価サンプル:")
    for k in ['R', 'HI', 'その他', 'RB', 'Rリ', '植物用', '圧搾カス']:
        if k in nayose_map:
            print(f"    {k}: ¥{int(nayose_map[k]):,}/kg")

    async with async_session_factory() as db:
        # 全 crude_products
        res = await db.execute(select(CrudeProduct.id, CrudeProduct.code, CrudeProduct.name))
        crudes = [(r[0], r[1], r[2]) for r in res.all()]
        print(f"\nDB crude_products: {len(crudes)}件")

        # 既存 CrudeProductStandardCost (period_id × crude_id)
        res = await db.execute(
            select(CrudeProductStandardCost.crude_product_id, CrudeProductStandardCost.unit_cost)
            .where(CrudeProductStandardCost.period_id == period_id)
        )
        existing = {r[0]: r[1] for r in res.all()}
        print(f"既存 CrudeProductStandardCost (this period): {len(existing)}件")

        # マッチング
        matched_direct = 0
        matched_nayose = 0
        no_match = []
        updated = 0
        inserted = 0
        for cid, code, name in crudes:
            if not name:
                no_match.append((code, name, 'no_name'))
                continue
            n = str(name).strip()
            price: Decimal | None = name_map.get(n)
            source = 'direct'
            if price is None:
                # 名寄推定
                nay = infer_nayose_from_name(n)
                if nay:
                    price = nayose_map.get(nay)
                    source = f'nayose={nay}'
            if price is None:
                no_match.append((code, n, 'no_match'))
                continue
            if source == 'direct':
                matched_direct += 1
            else:
                matched_nayose += 1

            # UPSERT
            if cid in existing:
                if Decimal(str(existing[cid])) != price:
                    # update
                    res = await db.execute(
                        select(CrudeProductStandardCost).where(
                            CrudeProductStandardCost.crude_product_id == cid,
                            CrudeProductStandardCost.period_id == period_id,
                        )
                    )
                    obj = res.scalar_one()
                    obj.material_cost = Decimal('0')
                    obj.labor_cost = Decimal('0')
                    obj.overhead_cost = Decimal('0')
                    obj.prior_process_cost = Decimal('0')
                    obj.total_cost = price
                    obj.unit_cost = price
                    obj.notes = f'仕掛品SC明細 ({source})'
                    updated += 1
            else:
                db.add(CrudeProductStandardCost(
                    crude_product_id=cid,
                    period_id=period_id,
                    material_cost=Decimal('0'),
                    labor_cost=Decimal('0'),
                    overhead_cost=Decimal('0'),
                    prior_process_cost=Decimal('0'),
                    total_cost=price,
                    unit_cost=price,
                    standard_quantity=Decimal('1'),
                    notes=f'仕掛品SC明細 ({source})',
                ))
                inserted += 1

        await db.flush()
        print(f"\n=== マッチング結果 ===")
        print(f"  直接マッチ(C列): {matched_direct}件")
        print(f"  名寄フォールバック(D列): {matched_nayose}件")
        print(f"  未マッチ: {len(no_match)}件")
        print(f"  CrudeProductStandardCost: INSERT {inserted}件 / UPDATE {updated}件")
        if no_match:
            print(f"  未マッチ サンプル: {no_match[:5]}")

        # 再計算
        n = await recalculate_valuation_amounts(db, period_id)
        print(f"\n=== recalculate ===")
        print(f"  updated: {n}")
        await db.commit()

        # サマリ
        crude_total = (await db.execute(select(func.count()).where(
            InventoryValuation.period_id == period_id,
            InventoryValuation.category == InventoryCategory.crude_product,
        ))).scalar()
        crude_priced = (await db.execute(select(func.count()).where(
            InventoryValuation.period_id == period_id,
            InventoryValuation.category == InventoryCategory.crude_product,
            InventoryValuation.standard_unit_price > 0,
        ))).scalar()
        crude_val = (await db.execute(select(func.sum(InventoryValuation.valuation_amount)).where(
            InventoryValuation.period_id == period_id,
            InventoryValuation.category == InventoryCategory.crude_product,
        ))).scalar()
        total_val = (await db.execute(select(func.sum(InventoryValuation.valuation_amount)).where(
            InventoryValuation.period_id == period_id,
        ))).scalar()
        print(f"\n=== AFTER ===")
        print(f"  crude inv records: {crude_total} / priced: {crude_priced}")
        print(f"  crude valuation: ¥{float(crude_val or 0):,.0f}")
        print(f"  全体 valuation: ¥{float(total_val or 0):,.0f}")


def main():
    parser = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    parser.add_argument('--period-id', required=True)
    parser.add_argument('--sc-xlsx', required=True, help='決算用SC仕掛品.xlsx')
    args = parser.parse_args()
    os.environ.setdefault('SECRET_KEY', 'dev')
    os.environ.setdefault('ANTHROPIC_API_KEY', 'dummy')
    asyncio.run(run(uuid.UUID(args.period_id), args.sc_xlsx))


if __name__ == '__main__':
    main()
