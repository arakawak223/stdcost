"""System reconciliation service (Phase 6).

複数ソースシステム間の実際原価データを突合し、差異を検出する。
"""

import uuid
from collections import defaultdict
from decimal import Decimal

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.audit import ReconciliationResult, ReconciliationStatus
from app.models.cost import ActualCost


async def reconcile_period(
    db: AsyncSession,
    period_id: uuid.UUID,
    threshold: Decimal = Decimal("1000"),
) -> list[ReconciliationResult]:
    """対象期間の実際原価データをソースシステム間で突合する。

    sc_system と kanjyo_bugyo のデータを比較し、
    差額が閾値以下ならmatched、超過ならdiscrepancy、片方のみならunmatched。
    """
    # 既存結果を削除（再実行対応）
    existing = await db.execute(
        select(ReconciliationResult).where(ReconciliationResult.period_id == period_id)
    )
    for r in existing.scalars().all():
        await db.delete(r)
    await db.flush()

    # 対象期間のActualCost全件を取得
    result = await db.execute(
        select(ActualCost).where(ActualCost.period_id == period_id)
    )
    all_costs = result.scalars().all()

    if not all_costs:
        return []

    # (product_id, source_system)でグルーピング
    by_product: dict[uuid.UUID, dict[str, ActualCost]] = defaultdict(dict)
    for cost in all_costs:
        by_product[cost.product_id][cost.source_system.value] = cost

    results: list[ReconciliationResult] = []

    for product_id, sources in by_product.items():
        sc_cost = sources.get("sc_system")
        bugyo_cost = sources.get("kanjyo_bugyo")

        if sc_cost and bugyo_cost:
            # 両方にデータあり → 比較
            value_a = sc_cost.total_cost
            value_b = bugyo_cost.total_cost
            diff = abs(value_a - value_b)

            if diff <= threshold:
                status = ReconciliationStatus.matched
            else:
                status = ReconciliationStatus.discrepancy

            rec = ReconciliationResult(
                period_id=period_id,
                entity_type="product",
                entity_id=str(product_id),
                source_a="sc_system",
                source_b="kanjyo_bugyo",
                value_a=value_a,
                value_b=value_b,
                difference=value_a - value_b,
                status=status,
            )
            db.add(rec)
            results.append(rec)

        elif sc_cost and not bugyo_cost:
            # SCのみ
            rec = ReconciliationResult(
                period_id=period_id,
                entity_type="product",
                entity_id=str(product_id),
                source_a="sc_system",
                source_b="kanjyo_bugyo",
                value_a=sc_cost.total_cost,
                value_b=None,
                difference=None,
                status=ReconciliationStatus.unmatched,
                notes="勘定奉行にデータなし",
            )
            db.add(rec)
            results.append(rec)

        elif bugyo_cost and not sc_cost:
            # 奉行のみ
            rec = ReconciliationResult(
                period_id=period_id,
                entity_type="product",
                entity_id=str(product_id),
                source_a="sc_system",
                source_b="kanjyo_bugyo",
                value_a=None,
                value_b=bugyo_cost.total_cost,
                difference=None,
                status=ReconciliationStatus.unmatched,
                notes="SCシステムにデータなし",
            )
            db.add(rec)
            results.append(rec)

    await db.flush()
    for r in results:
        await db.refresh(r)

    return results


async def get_reconciliation_summary(
    db: AsyncSession,
    period_id: uuid.UUID,
) -> dict:
    """突合結果のサマリーを返す。"""
    result = await db.execute(
        select(ReconciliationResult).where(ReconciliationResult.period_id == period_id)
    )
    records = result.scalars().all()

    summary = {
        "period_id": period_id,
        "total": len(records),
        "matched": sum(1 for r in records if r.status == ReconciliationStatus.matched),
        "unmatched": sum(1 for r in records if r.status == ReconciliationStatus.unmatched),
        "discrepancy": sum(1 for r in records if r.status == ReconciliationStatus.discrepancy),
    }
    return summary
