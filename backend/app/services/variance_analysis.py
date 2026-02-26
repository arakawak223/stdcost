"""Variance analysis service — 標準原価 vs 実際原価の差異を計算・記録する。

差異分析のロジック:
  1. 期間内の標準原価と実際原価を突合
  2. 原価要素別に差異額・差異率を算出
  3. 有利/不利差異の判定
  4. 閾値超過の自動フラグ
"""

import uuid
from decimal import Decimal, ROUND_HALF_UP

from sqlalchemy import delete, select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.cost import ActualCost, StandardCost
from app.models.master import CostCenter, Product
from app.models.variance import VarianceRecord, VarianceType

D = Decimal
ZERO = D("0")
FOUR = D("0.0001")
HUNDRED = D("100")

# Cost elements to compare between StandardCost and ActualCost
COST_ELEMENTS = [
    ("crude_product_cost", "原体原価"),
    ("packaging_cost", "資材費"),
    ("labor_cost", "労務費"),
    ("overhead_cost", "経費"),
    ("outsourcing_cost", "外注加工費"),
]


async def analyze_variances(
    db: AsyncSession,
    period_id: uuid.UUID,
    product_ids: list[uuid.UUID] | None = None,
    threshold_percent: Decimal = D("5.0"),
) -> dict:
    """標準原価と実際原価を比較し、差異レコードを作成する。

    Returns dict with analysis result for API response.
    """
    # Load standard costs for the period
    std_query = select(StandardCost).where(StandardCost.period_id == period_id)
    if product_ids:
        std_query = std_query.where(StandardCost.product_id.in_(product_ids))
    std_result = await db.execute(std_query)
    standard_costs = {str(sc.product_id): sc for sc in std_result.scalars().all()}

    # Load actual costs for the period
    act_query = select(ActualCost).where(ActualCost.period_id == period_id)
    if product_ids:
        act_query = act_query.where(ActualCost.product_id.in_(product_ids))
    act_result = await db.execute(act_query)
    actual_costs_list = list(act_result.scalars().all())

    # Group actual costs by product_id (may have multiple cost centers)
    actual_by_product: dict[str, list[ActualCost]] = {}
    for ac in actual_costs_list:
        pid = str(ac.product_id)
        actual_by_product.setdefault(pid, []).append(ac)

    # Load product info for response
    prod_result = await db.execute(select(Product))
    products_map = {str(p.id): p for p in prod_result.scalars().all()}

    # Load cost center info for response
    cc_result = await db.execute(select(CostCenter))
    cc_map = {str(cc.id): cc for cc in cc_result.scalars().all()}

    # Delete existing variance records for this period/products to avoid duplicates
    del_query = delete(VarianceRecord).where(VarianceRecord.period_id == period_id)
    if product_ids:
        del_query = del_query.where(VarianceRecord.product_id.in_(product_ids))
    await db.execute(del_query)

    # Find products that have both standard and actual costs
    all_product_ids = set(standard_costs.keys()) & set(actual_by_product.keys())

    records_created = 0
    flagged_count = 0
    total_standard = ZERO
    total_actual = ZERO
    details: list[dict] = []

    for pid in sorted(all_product_ids):
        sc = standard_costs[pid]
        actuals = actual_by_product[pid]
        prod = products_map.get(pid)

        # Aggregate actual costs across all cost centers for this product
        agg_actual = _aggregate_actual_costs(actuals)

        prod_total_std = ZERO
        prod_total_act = ZERO
        elements: list[dict] = []

        for field_name, element_label in COST_ELEMENTS:
            std_val = D(str(getattr(sc, field_name, 0) or 0))
            act_val = D(str(agg_actual.get(field_name, 0) or 0))
            variance = act_val - std_val
            pct = _calc_percent(variance, std_val)
            favorable = variance <= ZERO  # Lower actual = favorable

            prod_total_std += std_val
            prod_total_act += act_val

            # Create variance record per cost element, per actual cost center
            for ac in actuals:
                ac_std = std_val  # Standard is at product level
                ac_act = D(str(getattr(ac, field_name, 0) or 0))
                ac_variance = ac_act - ac_std
                ac_pct = _calc_percent(ac_variance, ac_std)
                ac_favorable = ac_variance <= ZERO

                is_flagged = abs(ac_pct) > threshold_percent
                flag_reason = None
                if is_flagged:
                    direction = "有利" if ac_favorable else "不利"
                    flag_reason = f"{element_label}の{direction}差異が閾値({threshold_percent}%)を超過: {ac_pct}%"

                record = VarianceRecord(
                    product_id=uuid.UUID(pid),
                    cost_center_id=ac.cost_center_id,
                    period_id=period_id,
                    variance_type=VarianceType.price,
                    cost_element=field_name,
                    standard_amount=ac_std,
                    actual_amount=ac_act,
                    variance_amount=ac_variance,
                    variance_percent=ac_pct,
                    is_favorable=ac_favorable,
                    is_flagged=is_flagged,
                    flag_reason=flag_reason,
                )
                db.add(record)
                records_created += 1
                if is_flagged:
                    flagged_count += 1

            elements.append({
                "cost_element": field_name,
                "standard_amount": std_val,
                "actual_amount": act_val,
                "variance_amount": variance,
                "variance_percent": pct,
                "is_favorable": favorable,
            })

        prod_variance = prod_total_act - prod_total_std
        prod_pct = _calc_percent(prod_variance, prod_total_std)

        # Use the first actual's cost center for summary (or None if aggregated)
        first_ac = actuals[0] if actuals else None
        cc_id = first_ac.cost_center_id if first_ac else None
        cc = cc_map.get(str(cc_id)) if cc_id else None

        details.append({
            "product_id": uuid.UUID(pid),
            "product_code": prod.code if prod else "",
            "product_name": prod.name if prod else "",
            "cost_center_id": cc_id,
            "cost_center_name": cc.name if cc else None,
            "total_standard": prod_total_std,
            "total_actual": prod_total_act,
            "total_variance": prod_variance,
            "total_variance_percent": prod_pct,
            "is_favorable": prod_variance <= ZERO,
            "elements": elements,
        })

        total_standard += prod_total_std
        total_actual += prod_total_act

    await db.flush()

    return {
        "period_id": period_id,
        "products_analyzed": len(all_product_ids),
        "records_created": records_created,
        "flagged_count": flagged_count,
        "total_standard": total_standard,
        "total_actual": total_actual,
        "total_variance": total_actual - total_standard,
        "details": details,
    }


async def get_variance_summary(
    db: AsyncSession,
    period_id: uuid.UUID,
) -> dict:
    """期間の差異サマリーレポートを生成する。"""
    result = await db.execute(
        select(VarianceRecord).where(VarianceRecord.period_id == period_id)
    )
    records = list(result.scalars().all())

    if not records:
        return {
            "period_id": period_id,
            "total_products": 0,
            "total_records": 0,
            "total_flagged": 0,
            "overall_standard": ZERO,
            "overall_actual": ZERO,
            "overall_variance": ZERO,
            "by_element": [],
        }

    product_ids = set()
    by_element: dict[str, dict] = {}

    for r in records:
        product_ids.add(str(r.product_id))
        elem = r.cost_element
        if elem not in by_element:
            by_element[elem] = {
                "cost_element": elem,
                "total_standard": ZERO,
                "total_actual": ZERO,
                "total_variance": ZERO,
                "variance_percents": [],
                "favorable_count": 0,
                "unfavorable_count": 0,
                "flagged_count": 0,
            }
        entry = by_element[elem]
        entry["total_standard"] += r.standard_amount
        entry["total_actual"] += r.actual_amount
        entry["total_variance"] += r.variance_amount
        entry["variance_percents"].append(r.variance_percent)
        if r.is_favorable:
            entry["favorable_count"] += 1
        else:
            entry["unfavorable_count"] += 1
        if r.is_flagged:
            entry["flagged_count"] += 1

    overall_std = sum(e["total_standard"] for e in by_element.values())
    overall_act = sum(e["total_actual"] for e in by_element.values())

    element_summaries = []
    for elem_data in by_element.values():
        pcts = elem_data.pop("variance_percents")
        avg_pct = (sum(pcts) / D(str(len(pcts)))).quantize(FOUR, ROUND_HALF_UP) if pcts else ZERO
        elem_data["average_variance_percent"] = avg_pct
        element_summaries.append(elem_data)

    return {
        "period_id": period_id,
        "total_products": len(product_ids),
        "total_records": len(records),
        "total_flagged": sum(1 for r in records if r.is_flagged),
        "overall_standard": overall_std,
        "overall_actual": overall_act,
        "overall_variance": overall_act - overall_std,
        "by_element": element_summaries,
    }


def _aggregate_actual_costs(actuals: list[ActualCost]) -> dict[str, Decimal]:
    """複数部門の実際原価を集約する。"""
    agg: dict[str, Decimal] = {}
    for field_name, _ in COST_ELEMENTS:
        total = ZERO
        for ac in actuals:
            total += D(str(getattr(ac, field_name, 0) or 0))
        agg[field_name] = total
    return agg


def _calc_percent(variance: Decimal, standard: Decimal) -> Decimal:
    """差異率を計算する。標準額が0の場合は0を返す。"""
    if standard == ZERO:
        return ZERO
    return ((variance / standard) * HUNDRED).quantize(FOUR, ROUND_HALF_UP)
