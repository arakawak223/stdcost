"""Allocation calculation helpers for distributing overhead costs.

Supports both simple quantity-based allocation and AllocationRule-based allocation.
"""

from datetime import datetime, timezone
from decimal import Decimal, ROUND_HALF_UP

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.cost import CostAllocation, CostElement
from app.models.master import AllocationBasis, AllocationRule

ZERO = Decimal("0")
FOUR = Decimal("0.0001")


def allocate_by_quantity(
    total_budget: Decimal,
    quantities: dict[str, Decimal],
) -> dict[str, Decimal]:
    """Allocate budget proportionally based on quantities.

    Args:
        total_budget: Total budget amount to allocate.
        quantities: Dict of {item_id: quantity} for allocation basis.

    Returns:
        Dict of {item_id: allocated_amount}.
    """
    total_qty = sum(quantities.values())
    if total_qty == 0:
        return {k: Decimal("0") for k in quantities}

    result: dict[str, Decimal] = {}
    allocated_sum = Decimal("0")
    items = list(quantities.items())

    for i, (item_id, qty) in enumerate(items):
        if i == len(items) - 1:
            # Last item gets the remainder to avoid rounding errors
            result[item_id] = total_budget - allocated_sum
        else:
            amount = (total_budget * qty / total_qty).quantize(
                Decimal("0.0001"), rounding=ROUND_HALF_UP
            )
            result[item_id] = amount
            allocated_sum += amount

    return result


async def load_allocation_rules(
    db: AsyncSession,
    source_cost_center_id,
) -> list[AllocationRule]:
    """Load active allocation rules for a given source cost center, ordered by priority desc."""
    result = await db.execute(
        select(AllocationRule).where(
            AllocationRule.source_cost_center_id == source_cost_center_id,
            AllocationRule.is_active == True,
        ).order_by(AllocationRule.priority.desc())
    )
    return list(result.scalars().unique().all())


def _find_matching_rule(
    rules: list[AllocationRule],
    cost_element: str,
) -> AllocationRule | None:
    """Find the best matching rule for a cost element.

    Priority: exact cost_element match > wildcard (NULL) rule.
    Within each group, higher priority value wins (already sorted).
    """
    wildcard_rule = None
    for rule in rules:
        if rule.cost_element == cost_element:
            return rule
        if rule.cost_element is None and wildcard_rule is None:
            wildcard_rule = rule
    return wildcard_rule


def compute_allocation_quantities(
    basis: AllocationBasis,
    item_data: dict[str, dict],
) -> dict[str, Decimal]:
    """Compute allocation quantities based on AllocationBasis.

    Args:
        basis: The allocation basis to use.
        item_data: Dict of {item_id: {raw_material_quantity, weight, crude_quantity, ...}}.

    Returns:
        Dict of {item_id: quantity} for allocation.
    """
    quantities: dict[str, Decimal] = {}

    for item_id, data in item_data.items():
        if basis == AllocationBasis.raw_material_quantity:
            quantities[item_id] = Decimal(str(data.get("raw_material_quantity", 0)))
        elif basis == AllocationBasis.weight_based:
            quantities[item_id] = Decimal(str(data.get("weight", 0)))
        elif basis == AllocationBasis.crude_quantity:
            quantities[item_id] = Decimal(str(data.get("crude_quantity", 0)))
        elif basis == AllocationBasis.production_hours:
            # Use production_hours if available; fall back to raw_material_quantity
            hours = data.get("production_hours")
            if hours is not None and Decimal(str(hours)) > 0:
                quantities[item_id] = Decimal(str(hours))
            else:
                quantities[item_id] = Decimal(str(data.get("raw_material_quantity", 0)))
        elif basis == AllocationBasis.manual:
            # Manual uses ratio from AllocationRuleTarget; handled separately.
            quantities[item_id] = ZERO
        else:
            quantities[item_id] = Decimal(str(data.get("raw_material_quantity", 0)))

    return quantities


def allocate_by_ratio(
    total_budget: Decimal,
    ratios: dict[str, Decimal],
) -> dict[str, Decimal]:
    """Allocate budget based on fixed ratios (for manual allocation).

    Args:
        total_budget: Total budget amount to allocate.
        ratios: Dict of {item_id: ratio} where ratios should sum to ~1.0.

    Returns:
        Dict of {item_id: allocated_amount}.
    """
    total_ratio = sum(ratios.values())
    if total_ratio == 0:
        return {k: ZERO for k in ratios}

    result: dict[str, Decimal] = {}
    allocated_sum = ZERO
    items = list(ratios.items())

    for i, (item_id, ratio) in enumerate(items):
        if i == len(items) - 1:
            result[item_id] = total_budget - allocated_sum
        else:
            amount = (total_budget * ratio / total_ratio).quantize(FOUR, ROUND_HALF_UP)
            result[item_id] = amount
            allocated_sum += amount

    return result


async def execute_rule_based_allocation(
    db: AsyncSession,
    source_cost_center_id,
    budgets: dict[str, Decimal],
    item_data: dict[str, dict],
    period_id=None,
    simulate: bool = True,
    default_basis: AllocationBasis = AllocationBasis.raw_material_quantity,
) -> dict[str, dict[str, Decimal]]:
    """Execute allocation using AllocationRules, falling back to default if no rules exist.

    Args:
        db: Database session.
        source_cost_center_id: The cost center whose budget is being allocated.
        budgets: Dict of {cost_element: amount} e.g. {"labor": 1000, "overhead": 2000}.
        item_data: Dict of {item_id: {raw_material_quantity, weight, crude_quantity, ...}}.
        period_id: Fiscal period ID (for CostAllocation records).
        simulate: If True, do not create CostAllocation records.
        default_basis: Fallback basis when no rules are defined.

    Returns:
        Dict of {cost_element: {item_id: allocated_amount}}.
    """
    rules = await load_allocation_rules(db, source_cost_center_id)

    result: dict[str, dict[str, Decimal]] = {}

    for cost_element, budget_amount in budgets.items():
        if budget_amount == ZERO:
            result[cost_element] = {item_id: ZERO for item_id in item_data}
            continue

        # Find the best matching rule: exact cost_element > wildcard (NULL) > no rule
        matching_rule = _find_matching_rule(rules, cost_element)

        if matching_rule and matching_rule.basis == AllocationBasis.manual:
            # Manual allocation: use target ratios
            # Map target_cost_center_id ratios to item_ids
            # For simplicity, if manual ratios are defined, use them directly
            target_ratios = {
                str(t.target_cost_center_id): t.ratio
                for t in matching_rule.targets
            }
            if target_ratios:
                allocation = allocate_by_ratio(budget_amount, target_ratios)
            else:
                # No targets defined, fall back to default
                quantities = compute_allocation_quantities(default_basis, item_data)
                allocation = allocate_by_quantity(budget_amount, quantities)
        elif matching_rule:
            # Rule-based allocation with computed quantities
            basis = matching_rule.basis
            quantities = compute_allocation_quantities(basis, item_data)
            allocation = allocate_by_quantity(budget_amount, quantities)
        else:
            # No rules: fall back to default behavior
            quantities = compute_allocation_quantities(default_basis, item_data)
            allocation = allocate_by_quantity(budget_amount, quantities)

        result[cost_element] = allocation

        # Create CostAllocation records (non-simulation only)
        if not simulate and period_id and matching_rule:
            await _create_allocation_records(
                db=db,
                rule=matching_rule,
                period_id=period_id,
                source_cost_center_id=source_cost_center_id,
                cost_element=cost_element,
                allocation=allocation,
                quantities=compute_allocation_quantities(
                    matching_rule.basis if matching_rule.basis != AllocationBasis.manual else default_basis,
                    item_data,
                ),
                budget_amount=budget_amount,
            )

    return result


async def _create_allocation_records(
    db: AsyncSession,
    rule: AllocationRule,
    period_id,
    source_cost_center_id,
    cost_element: str,
    allocation: dict[str, Decimal],
    quantities: dict[str, Decimal],
    budget_amount: Decimal,
) -> None:
    """Create CostAllocation records for audit trail."""
    total_qty = sum(quantities.values())

    # Map cost_element string to CostElement enum
    element_map = {e.value: e for e in CostElement}
    ce = element_map.get(cost_element)

    for item_id, amount in allocation.items():
        if amount == ZERO:
            continue
        qty = quantities.get(item_id, ZERO)
        ratio = (qty / total_qty).quantize(FOUR, ROUND_HALF_UP) if total_qty > 0 else ZERO

        record = CostAllocation(
            rule_id=rule.id,
            period_id=period_id,
            source_cost_center_id=source_cost_center_id,
            target_cost_center_id=source_cost_center_id,  # Same center in this context
            cost_element=ce,
            allocated_amount=amount,
            basis_quantity=qty,
            ratio=ratio,
            executed_at=datetime.now(timezone.utc),
        )
        db.add(record)
