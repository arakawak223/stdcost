"""Inventory valuation service — 標準単価×実際数量で在庫金額・払出金額を計算する。

主な機能:
  1. 期末在庫評価サマリ(区分別・倉庫別集計)
  2. 製品在庫推移(期首+受入-払出=期末) — 標準単価ベース
  3. 標準単価マスタ更新後の在庫評価金額の再計算
"""

import uuid
from collections import defaultdict
from decimal import Decimal

from sqlalchemy import func, select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.cost import (
    CrudeProductStandardCost,
    InventoryCategory,
    InventoryMovement,
    InventoryValuation,
    MovementType,
    StandardCost,
)
from app.models.master import CrudeProduct, FiscalPeriod, Material, Product
from app.schemas.inventory_valuation import (
    CategorySummary,
    ProductInventoryFlow,
    ValuationSummary,
    WarehouseSummary,
)


# 受入と判定する MovementType
RECEIPT_MOVEMENT_TYPES = {
    MovementType.material_receipt,
    MovementType.crude_increase,
    MovementType.crude_input,
    MovementType.finished_goods,
}

# 払出と判定する MovementType
ISSUE_MOVEMENT_TYPES = {
    MovementType.material_usage,
    MovementType.crude_output,
    MovementType.research,
    MovementType.promotion,
    MovementType.adjustment,
}


async def get_valuation_summary(
    db: AsyncSession, period_id: uuid.UUID
) -> ValuationSummary:
    """指定期間の在庫評価サマリを返す（区分別・倉庫別集計）。"""
    # 区分別集計
    cat_result = await db.execute(
        select(
            InventoryValuation.category,
            func.count(InventoryValuation.id),
            func.coalesce(func.sum(InventoryValuation.quantity), 0),
            func.coalesce(func.sum(InventoryValuation.valuation_amount), 0),
        )
        .where(InventoryValuation.period_id == period_id)
        .group_by(InventoryValuation.category)
    )
    by_category = [
        CategorySummary(
            category=row[0],
            item_count=row[1],
            total_quantity=Decimal(str(row[2])),
            total_amount=Decimal(str(row[3])),
        )
        for row in cat_result.all()
    ]

    # 倉庫別集計
    wh_result = await db.execute(
        select(
            InventoryValuation.warehouse_name,
            func.count(InventoryValuation.id),
            func.coalesce(func.sum(InventoryValuation.valuation_amount), 0),
        )
        .where(InventoryValuation.period_id == period_id)
        .group_by(InventoryValuation.warehouse_name)
        .order_by(func.sum(InventoryValuation.valuation_amount).desc())
    )
    by_warehouse = [
        WarehouseSummary(
            warehouse_name=row[0],
            item_count=row[1],
            total_amount=Decimal(str(row[2])),
        )
        for row in wh_result.all()
    ]

    # 全体合計
    total_result = await db.execute(
        select(
            func.count(InventoryValuation.id),
            func.coalesce(func.sum(InventoryValuation.valuation_amount), 0),
        ).where(InventoryValuation.period_id == period_id)
    )
    total_items, total_amount = total_result.one()

    return ValuationSummary(
        period_id=period_id,
        total_items=total_items,
        total_amount=Decimal(str(total_amount)),
        by_category=by_category,
        by_warehouse=by_warehouse,
    )


async def get_product_inventory_flow(
    db: AsyncSession,
    period_id: uuid.UUID,
    prior_period_id: uuid.UUID | None = None,
) -> list[ProductInventoryFlow]:
    """製品ごとの期首+受入-払出=期末の在庫推移を標準単価ベースで返す。

    - 期首: prior_period_id の InventoryValuation の数量合計
    - 受入: 当期 InventoryMovement で受入区分の数量合計
    - 払出: 当期 InventoryMovement で払出区分の数量合計
    - 期末: 当期 InventoryValuation の数量合計
    - 金額 = 数量 × StandardCost.unit_cost(当期)
    """
    # 標準単価マップ
    std_result = await db.execute(
        select(StandardCost.product_id, StandardCost.unit_cost).where(
            StandardCost.period_id == period_id
        )
    )
    std_map: dict[uuid.UUID, Decimal] = {row[0]: row[1] for row in std_result.all()}

    # 当期の期末在庫数量（製品単位で集計）
    end_result = await db.execute(
        select(
            InventoryValuation.product_id,
            func.coalesce(func.sum(InventoryValuation.quantity), 0),
        )
        .where(
            InventoryValuation.period_id == period_id,
            InventoryValuation.product_id.is_not(None),
            InventoryValuation.category.in_(
                [InventoryCategory.product, InventoryCategory.semi_finished, InventoryCategory.merchandise]
            ),
        )
        .group_by(InventoryValuation.product_id)
    )
    ending_map: dict[uuid.UUID, Decimal] = {
        row[0]: Decimal(str(row[1])) for row in end_result.all()
    }

    # 前期の期末在庫数量(=当期期首)
    beginning_map: dict[uuid.UUID, Decimal] = {}
    if prior_period_id:
        begin_result = await db.execute(
            select(
                InventoryValuation.product_id,
                func.coalesce(func.sum(InventoryValuation.quantity), 0),
            )
            .where(
                InventoryValuation.period_id == prior_period_id,
                InventoryValuation.product_id.is_not(None),
                InventoryValuation.category.in_(
                    [InventoryCategory.product, InventoryCategory.semi_finished, InventoryCategory.merchandise]
                ),
            )
            .group_by(InventoryValuation.product_id)
        )
        beginning_map = {row[0]: Decimal(str(row[1])) for row in begin_result.all()}

    # 当期の受入・払出数量
    receipt_map: dict[uuid.UUID, Decimal] = defaultdict(lambda: Decimal("0"))
    issue_map: dict[uuid.UUID, Decimal] = defaultdict(lambda: Decimal("0"))

    mv_result = await db.execute(
        select(
            InventoryMovement.product_id,
            InventoryMovement.movement_type,
            func.coalesce(func.sum(InventoryMovement.quantity), 0),
        )
        .where(
            InventoryMovement.period_id == period_id,
            InventoryMovement.product_id.is_not(None),
        )
        .group_by(InventoryMovement.product_id, InventoryMovement.movement_type)
    )
    for product_id, mv_type, qty in mv_result.all():
        qty_dec = Decimal(str(qty))
        if mv_type in RECEIPT_MOVEMENT_TYPES:
            receipt_map[product_id] += qty_dec
        elif mv_type in ISSUE_MOVEMENT_TYPES:
            issue_map[product_id] += qty_dec

    # 製品マスタを引いて結果を組み立て
    all_pids = set(ending_map) | set(beginning_map) | set(receipt_map) | set(issue_map)
    if not all_pids:
        return []

    prod_result = await db.execute(
        select(Product.id, Product.code, Product.name).where(Product.id.in_(all_pids))
    )
    prod_map = {row[0]: (row[1], row[2]) for row in prod_result.all()}

    flows: list[ProductInventoryFlow] = []
    for pid in all_pids:
        code, name = prod_map.get(pid, (str(pid), ""))
        unit_price = Decimal(str(std_map.get(pid, 0)))
        b_qty = beginning_map.get(pid, Decimal("0"))
        r_qty = receipt_map.get(pid, Decimal("0"))
        i_qty = issue_map.get(pid, Decimal("0"))
        e_qty = ending_map.get(pid, Decimal("0"))
        flows.append(ProductInventoryFlow(
            product_id=pid,
            product_code=code,
            product_name=name,
            standard_unit_price=unit_price,
            beginning_qty=b_qty,
            receipt_qty=r_qty,
            issue_qty=i_qty,
            ending_qty=e_qty,
            beginning_amount=b_qty * unit_price,
            receipt_amount=r_qty * unit_price,
            issue_amount=i_qty * unit_price,
            ending_amount=e_qty * unit_price,
        ))
    flows.sort(key=lambda f: f.product_code)
    return flows


async def recalculate_valuation_amounts(
    db: AsyncSession, period_id: uuid.UUID
) -> int:
    """指定期間の InventoryValuation の標準単価をマスタから再取得し、評価金額を再計算する。

    マスタの単価が更新された後に呼び出すことを想定。
    """
    # マスタ単価を取得
    std_result = await db.execute(
        select(StandardCost.product_id, StandardCost.unit_cost).where(
            StandardCost.period_id == period_id
        )
    )
    std_map = {row[0]: Decimal(str(row[1])) for row in std_result.all()}

    crude_result = await db.execute(
        select(
            CrudeProductStandardCost.crude_product_id,
            CrudeProductStandardCost.unit_cost,
        ).where(CrudeProductStandardCost.period_id == period_id)
    )
    crude_map = {row[0]: Decimal(str(row[1])) for row in crude_result.all()}

    mat_result = await db.execute(
        select(Material.id, Material.standard_unit_price)
    )
    mat_map = {row[0]: Decimal(str(row[1])) for row in mat_result.all()}

    # 全件取得して再計算
    inv_result = await db.execute(
        select(InventoryValuation).where(InventoryValuation.period_id == period_id)
    )
    invs = inv_result.scalars().all()

    updated = 0
    for inv in invs:
        new_price: Decimal | None = None
        if inv.product_id and inv.product_id in std_map:
            new_price = std_map[inv.product_id]
        elif inv.crude_product_id and inv.crude_product_id in crude_map:
            new_price = crude_map[inv.crude_product_id]
        elif inv.material_id and inv.material_id in mat_map:
            new_price = mat_map[inv.material_id]

        if new_price is not None and new_price != inv.standard_unit_price:
            inv.standard_unit_price = new_price
            inv.valuation_amount = inv.quantity * new_price
            updated += 1
        elif new_price is not None:
            # 単価変わらないが、念のため金額再計算
            recalc = inv.quantity * new_price
            if recalc != inv.valuation_amount:
                inv.valuation_amount = recalc
                updated += 1

    await db.flush()
    return updated
