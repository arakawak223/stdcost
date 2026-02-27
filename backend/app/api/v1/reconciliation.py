"""Reconciliation API — ソースシステム間の突合チェック (Phase 6)。"""

import uuid

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.db.session import get_db
from app.models.audit import ReconciliationResult, ReconciliationStatus
from app.schemas.reconciliation import (
    ReconcileRequest,
    ReconcileResponse,
    ReconciliationResultRead,
    ReconciliationSummary,
)
from app.services.reconciliation import get_reconciliation_summary, reconcile_period

router = APIRouter()


@router.post("/run", response_model=ReconcileResponse)
async def run_reconciliation(
    data: ReconcileRequest, db: AsyncSession = Depends(get_db)
):
    """ソースシステム間の突合を実行する。"""
    results = await reconcile_period(db, data.period_id, data.threshold)
    summary_data = await get_reconciliation_summary(db, data.period_id)
    summary = ReconciliationSummary(**summary_data)

    return ReconcileResponse(
        summary=summary,
        results=[ReconciliationResultRead.model_validate(r) for r in results],
        message=f"突合完了: {summary.total}件 (一致: {summary.matched}, 不一致: {summary.discrepancy}, 未照合: {summary.unmatched})",
    )


@router.get("/results", response_model=list[ReconciliationResultRead])
async def list_reconciliation_results(
    period_id: uuid.UUID | None = None,
    status: ReconciliationStatus | None = None,
    db: AsyncSession = Depends(get_db),
):
    """突合結果一覧を取得する。"""
    query = select(ReconciliationResult)
    if period_id:
        query = query.where(ReconciliationResult.period_id == period_id)
    if status:
        query = query.where(ReconciliationResult.status == status)
    query = query.order_by(ReconciliationResult.entity_type, ReconciliationResult.entity_id)
    result = await db.execute(query)
    return result.scalars().all()


@router.get("/summary", response_model=ReconciliationSummary)
async def reconciliation_summary(
    period_id: uuid.UUID,
    db: AsyncSession = Depends(get_db),
):
    """突合サマリーレポートを取得する。"""
    summary_data = await get_reconciliation_summary(db, period_id)
    return ReconciliationSummary(**summary_data)
