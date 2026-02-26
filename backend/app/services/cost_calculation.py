"""Standard cost calculation engine.

2-stage standard cost calculation:
  Stage 1: 製造部（原体原価） - raw materials → crude products
  Stage 2: 製品課（製品原価） - crude products + packaging → finished products
"""

from decimal import Decimal, ROUND_HALF_UP

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.cost import CrudeProductStandardCost, StandardCost
from app.models.master import (
    AllocationBasis,
    BomHeader,
    BomType,
    CostBudget,
    CostCenter,
    CostCenterType,
    CrudeProduct,
    FiscalPeriod,
    Material,
    Product,
)
from app.services.allocation import allocate_by_quantity, execute_rule_based_allocation

D = Decimal
ZERO = D("0")
FOUR = D("0.0001")


def _resolve_material_price(
    mat,
    material_price_overrides: dict,
    category_rate_changes: dict,
) -> Decimal:
    """Resolve material price with priority: individual override > category rate > standard price."""
    mat_id_str = str(mat.id)
    if mat_id_str in material_price_overrides:
        return D(str(material_price_overrides[mat_id_str]))
    base_price = mat.standard_unit_price
    if category_rate_changes and mat.category:
        cat_key = mat.category.value if hasattr(mat.category, "value") else str(mat.category)
        if cat_key in category_rate_changes:
            return (D(str(base_price)) * D(str(category_rate_changes[cat_key]))).quantize(FOUR, ROUND_HALF_UP)
    return D(str(base_price))


async def _load_bom_headers(db: AsyncSession, bom_type: BomType) -> list[BomHeader]:
    result = await db.execute(
        select(BomHeader)
        .where(BomHeader.bom_type == bom_type, BomHeader.is_active == True)
        .order_by(BomHeader.effective_date.desc())
    )
    return list(result.scalars().unique().all())


async def _load_budgets(db: AsyncSession, period_id, center_type: CostCenterType) -> CostBudget | None:
    result = await db.execute(
        select(CostBudget)
        .join(CostCenter, CostBudget.cost_center_id == CostCenter.id)
        .where(
            CostBudget.period_id == period_id,
            CostCenter.center_type == center_type,
        )
    )
    return result.scalar_one_or_none()


async def calculate_standard_costs(
    db: AsyncSession,
    period_id,
    product_ids: list | None = None,
    simulate: bool = False,
    overrides: dict | None = None,
) -> dict:
    """Main entry point: calculate standard costs for a given period.

    Returns dict with crude_product_costs and product_costs lists.
    """
    overrides = overrides or {}
    material_price_overrides = overrides.get("material_prices", {})
    budget_overrides = overrides.get("budget_changes", {})
    category_rate_changes = overrides.get("category_rate_changes", {})

    # Load all materials for price lookup
    mat_result = await db.execute(select(Material).where(Material.is_active == True))
    materials = {str(m.id): m for m in mat_result.scalars().all()}

    # Load all crude products
    cp_result = await db.execute(select(CrudeProduct).where(CrudeProduct.is_active == True))
    crude_products = {str(cp.id): cp for cp in cp_result.scalars().all()}

    # Load all products
    prod_result = await db.execute(select(Product).where(Product.is_active == True))
    all_products = {str(p.id): p for p in prod_result.scalars().all()}

    # ===== Stage 1: 原体原価計算 =====
    stage1_boms = await _load_bom_headers(db, BomType.raw_material_process)

    # Group BOMs by crude_product_id (one BOM per crude product)
    cp_bom_map: dict[str, BomHeader] = {}
    for bom in stage1_boms:
        cp_id = str(bom.crude_product_id) if bom.crude_product_id else None
        if cp_id and cp_id not in cp_bom_map:
            cp_bom_map[cp_id] = bom

    # Load manufacturing budget
    mfg_budget = await _load_budgets(db, period_id, CostCenterType.manufacturing)
    mfg_labor = ZERO
    mfg_overhead = ZERO
    if mfg_budget:
        mfg_labor = mfg_budget.labor_budget
        mfg_overhead = mfg_budget.overhead_budget

    # Apply budget overrides
    if mfg_budget and str(mfg_budget.cost_center_id) in budget_overrides:
        bc = budget_overrides[str(mfg_budget.cost_center_id)]
        if "labor_budget" in bc:
            mfg_labor = D(str(bc["labor_budget"]))
        if "overhead_budget" in bc:
            mfg_overhead = D(str(bc["overhead_budget"]))

    # Calculate standard quantities for each crude product (for budget allocation)
    cp_std_quantities: dict[str, D] = {}
    cp_item_data: dict[str, dict] = {}
    for cp_id, bom in cp_bom_map.items():
        total_qty = ZERO
        for line in bom.lines:
            if line.material_id:
                total_qty += line.quantity * (D("1") + line.loss_rate)
        cp_std_quantities[cp_id] = total_qty
        cp_item_data[cp_id] = {"raw_material_quantity": total_qty}

    # Allocate labor and overhead budgets via rule-based allocation
    mfg_center_id = mfg_budget.cost_center_id if mfg_budget else None
    if mfg_center_id:
        stage1_alloc = await execute_rule_based_allocation(
            db=db,
            source_cost_center_id=mfg_center_id,
            budgets={"labor": mfg_labor, "overhead": mfg_overhead},
            item_data=cp_item_data,
            period_id=period_id,
            simulate=simulate,
            default_basis=AllocationBasis.raw_material_quantity,
        )
        labor_alloc = stage1_alloc["labor"]
        overhead_alloc = stage1_alloc["overhead"]
    else:
        labor_alloc = allocate_by_quantity(mfg_labor, cp_std_quantities)
        overhead_alloc = allocate_by_quantity(mfg_overhead, cp_std_quantities)

    # Calculate material costs for each crude product
    # Process non-blend first, then blend
    crude_cost_results: dict[str, dict] = {}

    # Sort: non-blend first
    sorted_cp_ids = sorted(
        cp_bom_map.keys(),
        key=lambda cid: (1 if crude_products.get(cid) and crude_products[cid].is_blend else 0, cid)
    )

    for cp_id in sorted_cp_ids:
        bom = cp_bom_map[cp_id]
        cp = crude_products.get(cp_id)
        if not cp:
            continue

        material_cost = ZERO
        prior_process_cost = ZERO

        for line in bom.lines:
            if line.material_id:
                mat_id_str = str(line.material_id)
                mat = materials.get(mat_id_str)
                if mat:
                    price = _resolve_material_price(mat, material_price_overrides, category_rate_changes)
                    material_cost += (price * line.quantity * (D("1") + line.loss_rate)).quantize(FOUR, ROUND_HALF_UP)

            elif line.crude_product_id:
                # Blend: use previously calculated crude product cost
                src_cp_id = str(line.crude_product_id)
                if src_cp_id in crude_cost_results:
                    src_unit_cost = crude_cost_results[src_cp_id]["unit_cost"]
                    prior_process_cost += (src_unit_cost * line.quantity).quantize(FOUR, ROUND_HALF_UP)

        labor = labor_alloc.get(cp_id, ZERO)
        overhead = overhead_alloc.get(cp_id, ZERO)
        total = material_cost + labor + overhead + prior_process_cost
        std_qty = cp_std_quantities.get(cp_id, D("1"))
        unit_cost = (total / std_qty).quantize(FOUR, ROUND_HALF_UP) if std_qty > 0 else ZERO

        crude_cost_results[cp_id] = {
            "crude_product_id": cp_id,
            "period_id": str(period_id),
            "material_cost": material_cost,
            "labor_cost": labor,
            "overhead_cost": overhead,
            "prior_process_cost": prior_process_cost,
            "total_cost": total,
            "unit_cost": unit_cost,
            "standard_quantity": std_qty,
        }

    # ===== Stage 2: 製品原価計算 =====
    stage2_boms = await _load_bom_headers(db, BomType.product_process)

    # Group BOMs by product_id
    prod_bom_map: dict[str, BomHeader] = {}
    for bom in stage2_boms:
        p_id = str(bom.product_id) if bom.product_id else None
        if p_id and p_id not in prod_bom_map:
            prod_bom_map[p_id] = bom

    # Filter by product_ids if provided
    if product_ids:
        pid_strs = {str(pid) for pid in product_ids}
        prod_bom_map = {k: v for k, v in prod_bom_map.items() if k in pid_strs}

    # Load product department budget
    prd_budget = await _load_budgets(db, period_id, CostCenterType.product)
    prd_labor = ZERO
    prd_overhead = ZERO
    prd_outsourcing = ZERO
    if prd_budget:
        prd_labor = prd_budget.labor_budget
        prd_overhead = prd_budget.overhead_budget
        prd_outsourcing = prd_budget.outsourcing_budget

    if prd_budget and str(prd_budget.cost_center_id) in budget_overrides:
        bc = budget_overrides[str(prd_budget.cost_center_id)]
        if "labor_budget" in bc:
            prd_labor = D(str(bc["labor_budget"]))
        if "overhead_budget" in bc:
            prd_overhead = D(str(bc["overhead_budget"]))
        if "outsourcing_budget" in bc:
            prd_outsourcing = D(str(bc["outsourcing_budget"]))

    # Calculate allocation basis: use content weight for each product
    prod_alloc_quantities: dict[str, D] = {}
    prod_item_data: dict[str, dict] = {}
    for p_id, bom in prod_bom_map.items():
        prod = all_products.get(p_id)
        if prod and prod.content_weight_g:
            weight = D(str(prod.content_weight_g))
        else:
            # Fallback: sum of BOM line quantities
            total_qty = ZERO
            for line in bom.lines:
                total_qty += line.quantity
            weight = total_qty if total_qty > 0 else D("1")
        prod_alloc_quantities[p_id] = weight
        prod_item_data[p_id] = {"weight": weight, "raw_material_quantity": weight}

    # Allocate product department budgets via rule-based allocation
    prd_center_id = prd_budget.cost_center_id if prd_budget else None
    if prd_center_id:
        stage2_alloc = await execute_rule_based_allocation(
            db=db,
            source_cost_center_id=prd_center_id,
            budgets={"labor": prd_labor, "overhead": prd_overhead, "outsourcing": prd_outsourcing},
            item_data=prod_item_data,
            period_id=period_id,
            simulate=simulate,
            default_basis=AllocationBasis.weight_based,
        )
        prod_labor_alloc = stage2_alloc["labor"]
        prod_overhead_alloc = stage2_alloc["overhead"]
        prod_outsourcing_alloc = stage2_alloc["outsourcing"]
    else:
        prod_labor_alloc = allocate_by_quantity(prd_labor, prod_alloc_quantities)
        prod_overhead_alloc = allocate_by_quantity(prd_overhead, prod_alloc_quantities)
        prod_outsourcing_alloc = allocate_by_quantity(prd_outsourcing, prod_alloc_quantities)

    product_cost_results: dict[str, dict] = {}

    for p_id, bom in prod_bom_map.items():
        prod = all_products.get(p_id)
        if not prod:
            continue

        crude_cost = ZERO
        packaging_cost = ZERO

        for line in bom.lines:
            if line.crude_product_id:
                cp_id_str = str(line.crude_product_id)
                if cp_id_str in crude_cost_results:
                    cp_unit = crude_cost_results[cp_id_str]["unit_cost"]
                    crude_cost += (cp_unit * line.quantity).quantize(FOUR, ROUND_HALF_UP)

            elif line.material_id:
                mat_id_str = str(line.material_id)
                mat = materials.get(mat_id_str)
                if mat:
                    price = _resolve_material_price(mat, material_price_overrides, category_rate_changes)
                    packaging_cost += (price * line.quantity * (D("1") + line.loss_rate)).quantize(FOUR, ROUND_HALF_UP)

        labor = prod_labor_alloc.get(p_id, ZERO)
        overhead = prod_overhead_alloc.get(p_id, ZERO)
        outsourcing = prod_outsourcing_alloc.get(p_id, ZERO)
        total = crude_cost + packaging_cost + labor + overhead + outsourcing
        lot_size = prod.standard_lot_size if prod.standard_lot_size and prod.standard_lot_size > 0 else D("1")
        unit_cost = (total / lot_size).quantize(FOUR, ROUND_HALF_UP)

        product_cost_results[p_id] = {
            "product_id": p_id,
            "period_id": str(period_id),
            "crude_product_cost": crude_cost,
            "packaging_cost": packaging_cost,
            "labor_cost": labor,
            "overhead_cost": overhead,
            "outsourcing_cost": outsourcing,
            "total_cost": total,
            "unit_cost": unit_cost,
            "lot_size": lot_size,
        }

    # ===== Save to DB (unless simulating) =====
    crude_cost_records = []
    product_cost_records = []

    if not simulate:
        for cp_data in crude_cost_results.values():
            existing = await db.execute(
                select(CrudeProductStandardCost).where(
                    CrudeProductStandardCost.crude_product_id == cp_data["crude_product_id"],
                    CrudeProductStandardCost.period_id == cp_data["period_id"],
                )
            )
            record = existing.scalar_one_or_none()
            if record:
                for k, v in cp_data.items():
                    if k not in ("crude_product_id", "period_id"):
                        setattr(record, k, v)
            else:
                record = CrudeProductStandardCost(**cp_data)
                db.add(record)
            await db.flush()
            await db.refresh(record)
            crude_cost_records.append(record)

        for p_data in product_cost_results.values():
            existing = await db.execute(
                select(StandardCost).where(
                    StandardCost.product_id == p_data["product_id"],
                    StandardCost.period_id == p_data["period_id"],
                )
            )
            record = existing.scalar_one_or_none()
            if record:
                for k, v in p_data.items():
                    if k not in ("product_id", "period_id"):
                        setattr(record, k, v)
            else:
                record = StandardCost(**p_data)
                db.add(record)
            await db.flush()
            await db.refresh(record)
            product_cost_records.append(record)

    return {
        "period_id": str(period_id),
        "crude_products_calculated": len(crude_cost_results),
        "products_calculated": len(product_cost_results),
        "total_crude_product_cost": sum(d["total_cost"] for d in crude_cost_results.values()),
        "total_product_cost": sum(d["total_cost"] for d in product_cost_results.values()),
        "crude_product_costs": crude_cost_records if not simulate else list(crude_cost_results.values()),
        "product_costs": product_cost_records if not simulate else list(product_cost_results.values()),
    }


async def copy_standard_costs(
    db: AsyncSession,
    source_period_id,
    target_period_id,
    overwrite: bool = False,
) -> dict:
    """Copy standard costs from source period to target period.

    Copies both CrudeProductStandardCost and StandardCost records.
    """
    if str(source_period_id) == str(target_period_id):
        raise ValueError("コピー元とコピー先の期間が同じです")

    # Verify periods exist
    for pid, label in [(source_period_id, "コピー元"), (target_period_id, "コピー先")]:
        result = await db.execute(select(FiscalPeriod).where(FiscalPeriod.id == pid))
        if not result.scalar_one_or_none():
            raise ValueError(f"{label}の会計期間が見つかりません: {pid}")

    counters = {
        "crude_product_costs_copied": 0,
        "crude_product_costs_skipped": 0,
        "crude_product_costs_updated": 0,
        "product_costs_copied": 0,
        "product_costs_skipped": 0,
        "product_costs_updated": 0,
    }

    # Copy CrudeProductStandardCost
    src_cp_result = await db.execute(
        select(CrudeProductStandardCost).where(
            CrudeProductStandardCost.period_id == source_period_id
        )
    )
    for src in src_cp_result.scalars().all():
        existing = await db.execute(
            select(CrudeProductStandardCost).where(
                CrudeProductStandardCost.crude_product_id == src.crude_product_id,
                CrudeProductStandardCost.period_id == target_period_id,
            )
        )
        target_record = existing.scalar_one_or_none()
        if target_record:
            if not overwrite:
                counters["crude_product_costs_skipped"] += 1
                continue
            for col in ("material_cost", "labor_cost", "overhead_cost",
                        "prior_process_cost", "total_cost", "unit_cost",
                        "standard_quantity", "notes"):
                setattr(target_record, col, getattr(src, col))
            counters["crude_product_costs_updated"] += 1
        else:
            new_record = CrudeProductStandardCost(
                crude_product_id=src.crude_product_id,
                period_id=target_period_id,
                material_cost=src.material_cost,
                labor_cost=src.labor_cost,
                overhead_cost=src.overhead_cost,
                prior_process_cost=src.prior_process_cost,
                total_cost=src.total_cost,
                unit_cost=src.unit_cost,
                standard_quantity=src.standard_quantity,
                notes=src.notes,
            )
            db.add(new_record)
            counters["crude_product_costs_copied"] += 1

    # Copy StandardCost
    src_prod_result = await db.execute(
        select(StandardCost).where(StandardCost.period_id == source_period_id)
    )
    for src in src_prod_result.scalars().all():
        existing = await db.execute(
            select(StandardCost).where(
                StandardCost.product_id == src.product_id,
                StandardCost.period_id == target_period_id,
            )
        )
        target_record = existing.scalar_one_or_none()
        if target_record:
            if not overwrite:
                counters["product_costs_skipped"] += 1
                continue
            for col in ("crude_product_cost", "packaging_cost", "labor_cost",
                        "overhead_cost", "outsourcing_cost", "total_cost",
                        "unit_cost", "lot_size", "notes"):
                setattr(target_record, col, getattr(src, col))
            counters["product_costs_updated"] += 1
        else:
            new_record = StandardCost(
                product_id=src.product_id,
                period_id=target_period_id,
                crude_product_cost=src.crude_product_cost,
                packaging_cost=src.packaging_cost,
                labor_cost=src.labor_cost,
                overhead_cost=src.overhead_cost,
                outsourcing_cost=src.outsourcing_cost,
                total_cost=src.total_cost,
                unit_cost=src.unit_cost,
                lot_size=src.lot_size,
                notes=src.notes,
            )
            db.add(new_record)
            counters["product_costs_copied"] += 1

    await db.flush()

    return {
        "source_period_id": str(source_period_id),
        "target_period_id": str(target_period_id),
        **counters,
    }
