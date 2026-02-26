"""Variance analysis API — 差異分析の実行・照会・レポート。"""

import uuid

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.db.session import get_db
from app.models.variance import VarianceRecord, VarianceType
from app.schemas.variance import (
    VarianceAnalysisRequest,
    VarianceAnalysisResult,
    VarianceRecordRead,
    VarianceRecordUpdate,
    VarianceSummaryReport,
)
from app.services.variance_analysis import analyze_variances, get_variance_summary

router = APIRouter()


@router.post("/analyze", response_model=VarianceAnalysisResult)
async def run_variance_analysis(
    data: VarianceAnalysisRequest, db: AsyncSession = Depends(get_db)
):
    """標準原価と実際原価の差異分析を実行する。"""
    result = await analyze_variances(
        db=db,
        period_id=data.period_id,
        product_ids=data.product_ids,
        threshold_percent=data.threshold_percent,
    )
    return result


@router.get("/summary", response_model=VarianceSummaryReport)
async def variance_summary(
    period_id: uuid.UUID,
    db: AsyncSession = Depends(get_db),
):
    """期間の差異サマリーレポートを取得する。"""
    result = await get_variance_summary(db=db, period_id=period_id)
    return result


@router.get("", response_model=list[VarianceRecordRead])
async def list_variance_records(
    period_id: uuid.UUID | None = None,
    product_id: uuid.UUID | None = None,
    cost_center_id: uuid.UUID | None = None,
    variance_type: VarianceType | None = None,
    cost_element: str | None = None,
    is_flagged: bool | None = None,
    db: AsyncSession = Depends(get_db),
):
    """差異レコード一覧を取得する。"""
    query = select(VarianceRecord)
    if period_id:
        query = query.where(VarianceRecord.period_id == period_id)
    if product_id:
        query = query.where(VarianceRecord.product_id == product_id)
    if cost_center_id:
        query = query.where(VarianceRecord.cost_center_id == cost_center_id)
    if variance_type:
        query = query.where(VarianceRecord.variance_type == variance_type)
    if cost_element:
        query = query.where(VarianceRecord.cost_element == cost_element)
    if is_flagged is not None:
        query = query.where(VarianceRecord.is_flagged == is_flagged)
    query = query.order_by(VarianceRecord.product_id, VarianceRecord.cost_element)
    result = await db.execute(query)
    return result.scalars().all()


@router.get("/{record_id}", response_model=VarianceRecordRead)
async def get_variance_record(
    record_id: uuid.UUID, db: AsyncSession = Depends(get_db)
):
    """差異レコードを取得する。"""
    result = await db.execute(
        select(VarianceRecord).where(VarianceRecord.id == record_id)
    )
    record = result.scalar_one_or_none()
    if not record:
        raise HTTPException(status_code=404, detail="差異レコードが見つかりません")
    return record


@router.put("/{record_id}", response_model=VarianceRecordRead)
async def update_variance_record(
    record_id: uuid.UUID,
    data: VarianceRecordUpdate,
    db: AsyncSession = Depends(get_db),
):
    """差異レコードのフラグ・メモを更新する。"""
    result = await db.execute(
        select(VarianceRecord).where(VarianceRecord.id == record_id)
    )
    record = result.scalar_one_or_none()
    if not record:
        raise HTTPException(status_code=404, detail="差異レコードが見つかりません")

    update_data = data.model_dump(exclude_unset=True)
    for field, value in update_data.items():
        setattr(record, field, value)
    await db.flush()
    await db.refresh(record)
    return record
