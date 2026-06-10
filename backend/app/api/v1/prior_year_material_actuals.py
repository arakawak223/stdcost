"""PriorYearMaterialActual API — 昨年実績(38期)原材料別SC原価の読出し。

書込は POST /imports/prior-year-materials (Excel取込) 経由のみ。
ここでは一覧/単件取得とサマリのみ提供する。
"""

import uuid

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy import func, select
from sqlalchemy.ext.asyncio import AsyncSession

from app.db.session import get_db
from app.models.cost import PriorYearMaterialActual
from app.schemas.prior_year_material_actual import (
    PriorYearMaterialActualRead,
    PriorYearMaterialActualSummary,
)

router = APIRouter()


@router.get("", response_model=list[PriorYearMaterialActualRead])
async def list_prior_year_material_actuals(
    fiscal_year: int | None = None,
    material_code: str | None = None,
    db: AsyncSession = Depends(get_db),
):
    """前年実績(原材料)の一覧。fiscal_year / material_code でフィルタ可能。"""
    query = select(PriorYearMaterialActual)
    if fiscal_year is not None:
        query = query.where(PriorYearMaterialActual.fiscal_year == fiscal_year)
    if material_code:
        query = query.where(PriorYearMaterialActual.material_code == material_code)
    query = query.order_by(
        PriorYearMaterialActual.fiscal_year, PriorYearMaterialActual.material_code
    )
    result = await db.execute(query)
    return result.scalars().all()


@router.get("/summary/{fiscal_year}", response_model=PriorYearMaterialActualSummary)
async def get_summary(fiscal_year: int, db: AsyncSession = Depends(get_db)):
    """fiscal_year 単位のサマリ統計。"""
    result = await db.execute(
        select(
            func.count(PriorYearMaterialActual.id),
            func.count(PriorYearMaterialActual.material_id),
            func.coalesce(func.sum(PriorYearMaterialActual.purchase_cost), 0),
            func.coalesce(func.sum(PriorYearMaterialActual.input_cost), 0),
            func.coalesce(func.sum(PriorYearMaterialActual.closing_cost), 0),
        ).where(PriorYearMaterialActual.fiscal_year == fiscal_year)
    )
    total_rows, matched_rows, purchase_sum, input_sum, close_sum = result.one()

    return PriorYearMaterialActualSummary(
        fiscal_year=fiscal_year,
        total_rows=int(total_rows or 0),
        matched_rows=int(matched_rows or 0),
        total_purchase_cost=purchase_sum,
        total_input_cost=input_sum,
        total_closing_cost=close_sum,
    )


@router.get("/{record_id}", response_model=PriorYearMaterialActualRead)
async def get_prior_year_material_actual(
    record_id: uuid.UUID, db: AsyncSession = Depends(get_db)
):
    result = await db.execute(
        select(PriorYearMaterialActual).where(PriorYearMaterialActual.id == record_id)
    )
    record = result.scalar_one_or_none()
    if not record:
        raise HTTPException(status_code=404, detail="前年実績(原材料)レコードが見つかりません")
    return record
