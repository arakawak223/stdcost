"""Phase 3-6 sample data seed.

Run: DATABASE_URL="postgresql+asyncpg://stdcost:stdcost_dev@localhost:5432/stdcost" python -m app.seed_phase3

Creates:
  1. StandardCost / CrudeProductStandardCost (via cost calculation engine)
  2. ActualCost (sc_system + kanjyo_bugyo — with realistic variations)
  3. CrudeProductActualCost (geneki_db)
  4. InventoryMovement (sample movements)
  5. ImportBatch (import history tracking)
"""

import asyncio
import random
import uuid
from datetime import date, datetime, timezone
from decimal import Decimal, ROUND_HALF_UP

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.db.session import async_session_factory
from app.models.audit import ImportBatch, ImportStatus, ReconciliationResult
from app.models.cost import (
    ActualCost,
    CrudeProductActualCost,
    CrudeProductStandardCost,
    InventoryMovement,
    MovementType,
    SourceSystem,
    StandardCost,
)
from app.models.master import (
    CostCenter,
    CrudeProduct,
    FiscalPeriod,
    Material,
    MaterialType,
    Product,
)
from app.models.variance import VarianceRecord
from app.services.cost_calculation import calculate_standard_costs

D = Decimal
ZERO = D("0")
FOUR = D("0.0001")

random.seed(42)  # Reproducible


def _vary(base: Decimal, low: float = -0.10, high: float = 0.15) -> Decimal:
    """Apply random variation to a base value."""
    factor = D(str(1 + random.uniform(low, high)))
    return (base * factor).quantize(FOUR, ROUND_HALF_UP)


def _vary_slight(base: Decimal) -> Decimal:
    """Small variation for reconciliation (sc vs bugyo)."""
    return _vary(base, -0.03, 0.03)


async def step1_calculate_standard_costs(db: AsyncSession) -> None:
    """Run standard cost calculation for 38th period months 1-5."""
    existing = await db.execute(select(StandardCost).limit(1))
    if existing.scalar_one_or_none():
        print("  標準原価: スキップ（既存データあり）")
        return

    periods = await db.execute(
        select(FiscalPeriod).where(
            FiscalPeriod.year == 38,
            FiscalPeriod.month <= 5,
        ).order_by(FiscalPeriod.month)
    )
    period_list = list(periods.scalars().all())

    total_crude = 0
    total_prod = 0
    for period in period_list:
        result = await calculate_standard_costs(db, period.id)
        total_crude += result["crude_products_calculated"]
        total_prod += result["products_calculated"]

    await db.flush()
    print(f"  標準原価: {len(period_list)}期間 × (原体{total_crude // len(period_list)}件 + 製品{total_prod // len(period_list)}件) 計算完了")


async def step2_seed_actual_costs(db: AsyncSession) -> None:
    """Create ActualCost records from sc_system and kanjyo_bugyo with variance."""
    existing = await db.execute(select(ActualCost).limit(1))
    if existing.scalar_one_or_none():
        print("  実際原価: スキップ（既存データあり）")
        return

    # Load references
    periods = await db.execute(
        select(FiscalPeriod).where(FiscalPeriod.year == 38, FiscalPeriod.month <= 5)
    )
    period_list = list(periods.scalars().all())

    cc_result = await db.execute(select(CostCenter))
    cc_map = {c.code: c for c in cc_result.scalars().all()}
    prd_center = cc_map["PRD"]

    # Standard costs by (product_id, period_id)
    std_result = await db.execute(select(StandardCost))
    std_costs = {(str(s.product_id), str(s.period_id)): s for s in std_result.scalars().all()}

    prod_result = await db.execute(select(Product).where(Product.is_active == True))
    products = list(prod_result.scalars().all())

    count = 0
    for period in period_list:
        for prod in products:
            key = (str(prod.id), str(period.id))
            sc = std_costs.get(key)
            if not sc:
                continue

            # Variation patterns per product type for realism
            # Some products have bigger labor variance, others material variance
            crude_var = _vary(sc.crude_product_cost, -0.08, 0.12)
            pkg_var = _vary(sc.packaging_cost, -0.05, 0.08)
            labor_var = _vary(sc.labor_cost, -0.10, 0.15)
            overhead_var = _vary(sc.overhead_cost, -0.07, 0.10)
            outsrc_var = _vary(sc.outsourcing_cost, -0.05, 0.12)
            total_sc = crude_var + pkg_var + labor_var + overhead_var + outsrc_var
            qty = D(str(random.randint(80, 150)))

            # SC system actual cost
            db.add(ActualCost(
                product_id=prod.id,
                cost_center_id=prd_center.id,
                period_id=period.id,
                crude_product_cost=crude_var,
                packaging_cost=pkg_var,
                labor_cost=labor_var,
                overhead_cost=overhead_var,
                outsourcing_cost=outsrc_var,
                total_cost=total_sc,
                quantity_produced=qty,
                source_system=SourceSystem.sc_system,
                notes="SCシステムからのインポート",
            ))
            count += 1

            # Kanjyo Bugyo — slight difference from SC for reconciliation testing
            # Some products match, some have small discrepancies, some have large ones
            dice = random.random()
            if dice < 0.4:
                # matched (within ¥1000)
                bugyo_crude = _vary_slight(crude_var)
                bugyo_pkg = _vary_slight(pkg_var)
                bugyo_labor = _vary_slight(labor_var)
                bugyo_overhead = _vary_slight(overhead_var)
                bugyo_outsrc = _vary_slight(outsrc_var)
            elif dice < 0.75:
                # small discrepancy
                bugyo_crude = _vary(crude_var, -0.05, 0.08)
                bugyo_pkg = _vary(pkg_var, -0.03, 0.05)
                bugyo_labor = _vary(labor_var, -0.08, 0.10)
                bugyo_overhead = _vary(overhead_var, -0.05, 0.08)
                bugyo_outsrc = _vary(outsrc_var, -0.03, 0.06)
            else:
                # large discrepancy — clearly different
                bugyo_crude = _vary(crude_var, -0.15, 0.25)
                bugyo_pkg = _vary(pkg_var, -0.10, 0.15)
                bugyo_labor = _vary(labor_var, -0.15, 0.25)
                bugyo_overhead = _vary(overhead_var, -0.10, 0.20)
                bugyo_outsrc = _vary(outsrc_var, -0.10, 0.20)

            bugyo_total = bugyo_crude + bugyo_pkg + bugyo_labor + bugyo_overhead + bugyo_outsrc

            # Use MFG center for bugyo to avoid unique constraint violation
            mfg_center = cc_map["MFG"]
            db.add(ActualCost(
                product_id=prod.id,
                cost_center_id=mfg_center.id,
                period_id=period.id,
                crude_product_cost=bugyo_crude,
                packaging_cost=bugyo_pkg,
                labor_cost=bugyo_labor,
                overhead_cost=bugyo_overhead,
                outsourcing_cost=bugyo_outsrc,
                total_cost=bugyo_total,
                quantity_produced=qty,
                source_system=SourceSystem.kanjyo_bugyo,
                notes="勘定奉行からのインポート",
            ))
            count += 1

    await db.flush()
    print(f"  実際原価: {count}件 作成 (SC+奉行 × {len(period_list)}期間 × {len(products)}製品)")


async def step3_seed_crude_actual_costs(db: AsyncSession) -> None:
    """Create CrudeProductActualCost records."""
    existing = await db.execute(select(CrudeProductActualCost).limit(1))
    if existing.scalar_one_or_none():
        print("  原体実際原価: スキップ（既存データあり）")
        return

    periods = await db.execute(
        select(FiscalPeriod).where(FiscalPeriod.year == 38, FiscalPeriod.month <= 5)
    )
    period_list = list(periods.scalars().all())

    crude_std_result = await db.execute(select(CrudeProductStandardCost))
    crude_stds = {(str(s.crude_product_id), str(s.period_id)): s for s in crude_std_result.scalars().all()}

    cp_result = await db.execute(select(CrudeProduct).where(CrudeProduct.is_active == True))
    crude_products = list(cp_result.scalars().all())

    count = 0
    for period in period_list:
        for cp in crude_products:
            key = (str(cp.id), str(period.id))
            cs = crude_stds.get(key)
            if not cs:
                continue

            mat_cost = _vary(cs.material_cost, -0.08, 0.12)
            labor_cost = _vary(cs.labor_cost, -0.10, 0.15)
            overhead_cost = _vary(cs.overhead_cost, -0.07, 0.10)
            prior_cost = _vary(cs.prior_process_cost, -0.05, 0.08) if cs.prior_process_cost > 0 else ZERO
            total = mat_cost + labor_cost + overhead_cost + prior_cost
            actual_qty = _vary(cs.standard_quantity, -0.05, 0.10)

            db.add(CrudeProductActualCost(
                crude_product_id=cp.id,
                period_id=period.id,
                material_cost=mat_cost,
                labor_cost=labor_cost,
                overhead_cost=overhead_cost,
                prior_process_cost=prior_cost,
                total_cost=total,
                actual_quantity=actual_qty,
                source_system=SourceSystem.geneki_db,
                notes="原液DBからのインポート",
            ))
            count += 1

    await db.flush()
    print(f"  原体実際原価: {count}件 作成")


async def step4_seed_inventory_movements(db: AsyncSession) -> None:
    """Create sample InventoryMovement records."""
    existing = await db.execute(select(InventoryMovement).limit(1))
    if existing.scalar_one_or_none():
        print("  在庫移動: スキップ（既存データあり）")
        return

    periods = await db.execute(
        select(FiscalPeriod).where(FiscalPeriod.year == 38, FiscalPeriod.month <= 5)
        .order_by(FiscalPeriod.month)
    )
    period_list = list(periods.scalars().all())

    cc_result = await db.execute(select(CostCenter))
    cc_map = {c.code: c for c in cc_result.scalars().all()}
    mfg = cc_map["MFG"]
    prd = cc_map["PRD"]

    mat_result = await db.execute(
        select(Material).where(Material.material_type == MaterialType.raw).limit(10)
    )
    materials = list(mat_result.scalars().all())

    cp_result = await db.execute(select(CrudeProduct).limit(5))
    crude_products = list(cp_result.scalars().all())

    prod_result = await db.execute(select(Product).limit(8))
    products = list(prod_result.scalars().all())

    count = 0
    for period in period_list:
        base_date = period.start_date

        # ① Material receipts (raw materials arriving)
        for mat in materials[:6]:
            qty = D(str(random.randint(50, 200)))
            unit_cost = mat.standard_unit_price * D(str(random.uniform(0.95, 1.10)))
            unit_cost = unit_cost.quantize(FOUR, ROUND_HALF_UP)
            db.add(InventoryMovement(
                material_id=mat.id,
                cost_center_id=mfg.id,
                period_id=period.id,
                movement_type=MovementType.material_receipt,
                movement_date=base_date.replace(day=min(3, 28)),
                quantity=qty,
                unit_cost=unit_cost,
                total_cost=(qty * unit_cost).quantize(FOUR),
                lot_number=f"LOT-{period.month:02d}-{mat.code}",
                source_system=SourceSystem.sc_system,
                notes=f"{mat.name} 入荷",
            ))
            count += 1

        # ② Material usage (raw materials → manufacturing)
        for mat in materials[:6]:
            qty = D(str(random.randint(30, 150)))
            unit_cost = mat.standard_unit_price
            db.add(InventoryMovement(
                material_id=mat.id,
                cost_center_id=mfg.id,
                period_id=period.id,
                movement_type=MovementType.material_usage,
                movement_date=base_date.replace(day=min(5, 28)),
                quantity=-qty,
                unit_cost=unit_cost,
                total_cost=(-qty * unit_cost).quantize(FOUR),
                source_system=SourceSystem.geneki_db,
                notes=f"{mat.name} 製造使用",
            ))
            count += 1

        # ③ Crude increase (fermentation complete)
        for cp in crude_products[:3]:
            qty = D(str(random.randint(20, 80)))
            unit_cost = D(str(random.randint(3000, 8000)))
            db.add(InventoryMovement(
                crude_product_id=cp.id,
                cost_center_id=mfg.id,
                period_id=period.id,
                movement_type=MovementType.crude_increase,
                movement_date=base_date.replace(day=min(15, 28)),
                quantity=qty,
                unit_cost=unit_cost,
                total_cost=(qty * unit_cost).quantize(FOUR),
                aging_start_date=base_date,
                lot_number=f"CR-{period.month:02d}-{cp.code}",
                source_system=SourceSystem.geneki_db,
                notes=f"{cp.name} 発酵完了",
            ))
            count += 1

        # ⑥ Finished goods (products complete)
        for prod in products[:5]:
            qty = D(str(random.randint(50, 200)))
            unit_cost = D(str(random.randint(500, 5000)))
            db.add(InventoryMovement(
                product_id=prod.id,
                cost_center_id=prd.id,
                period_id=period.id,
                movement_type=MovementType.finished_goods,
                movement_date=base_date.replace(day=min(20, 28)),
                quantity=qty,
                unit_cost=unit_cost,
                total_cost=(qty * unit_cost).quantize(FOUR),
                lot_number=f"FG-{period.month:02d}-{prod.code}",
                source_system=SourceSystem.sc_system,
                notes=f"{prod.name} 完成品入庫",
            ))
            count += 1

        # ⑦ Research use (small qty)
        if products:
            prod = random.choice(products[:3])
            qty = D(str(random.randint(5, 20)))
            db.add(InventoryMovement(
                product_id=prod.id,
                cost_center_id=cc_map["RND"].id,
                period_id=period.id,
                movement_type=MovementType.research,
                movement_date=base_date.replace(day=min(10, 28)),
                quantity=-qty,
                unit_cost=D("1000"),
                total_cost=(-qty * D("1000")).quantize(FOUR),
                source_system=SourceSystem.manual,
                notes="試験研究用出庫",
            ))
            count += 1

    await db.flush()
    print(f"  在庫移動: {count}件 作成")


async def step5_seed_import_batches(db: AsyncSession) -> None:
    """Create ImportBatch records for import history."""
    existing = await db.execute(select(ImportBatch).limit(1))
    if existing.scalar_one_or_none():
        print("  インポート履歴: スキップ（既存データあり）")
        return

    periods = await db.execute(
        select(FiscalPeriod).where(FiscalPeriod.year == 38, FiscalPeriod.month <= 5)
    )
    period_list = list(periods.scalars().all())

    prod_result = await db.execute(select(Product).where(Product.is_active == True))
    product_count = len(list(prod_result.scalars().all()))

    count = 0
    for period in period_list:
        now = datetime.now(timezone.utc)

        # SC system import
        db.add(ImportBatch(
            file_name=f"sc_actual_cost_{period.year}_{period.month:02d}.csv",
            source_system="sc_system",
            status=ImportStatus.completed,
            total_rows=product_count,
            success_rows=product_count,
            error_rows=0,
            period_id=period.id,
            started_at=now,
            completed_at=now,
            notes=f"第{period.year}期第{period.month}月 SCシステム実績取込",
        ))
        count += 1

        # Kanjyo Bugyo import
        db.add(ImportBatch(
            file_name=f"kanjyo_bugyo_{period.year}_{period.month:02d}.csv",
            source_system="kanjyo_bugyo",
            status=ImportStatus.completed,
            total_rows=product_count,
            success_rows=product_count,
            error_rows=0,
            period_id=period.id,
            started_at=now,
            completed_at=now,
            notes=f"第{period.year}期第{period.month}月 勘定奉行実績取込",
        ))
        count += 1

        # Geneki DB import
        db.add(ImportBatch(
            file_name=f"geneki_db_{period.year}_{period.month:02d}.xlsx",
            source_system="geneki_db",
            status=ImportStatus.completed,
            total_rows=14,
            success_rows=14,
            error_rows=0,
            period_id=period.id,
            started_at=now,
            completed_at=now,
            notes=f"第{period.year}期第{period.month}月 原液DB実績取込",
        ))
        count += 1

    await db.flush()
    print(f"  インポート履歴: {count}件 作成")


async def main() -> None:
    print("Phase 3-6 サンプルデータ投入開始...")
    async with async_session_factory() as db:
        await step1_calculate_standard_costs(db)
        await step2_seed_actual_costs(db)
        await step3_seed_crude_actual_costs(db)
        await step4_seed_inventory_movements(db)
        await step5_seed_import_batches(db)
        await db.commit()
    print("Phase 3-6 サンプルデータ投入完了!")


if __name__ == "__main__":
    asyncio.run(main())
