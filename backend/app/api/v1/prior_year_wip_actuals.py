"""PriorYearWipActual API — 昨年実績(38期)仕掛品別SC原価の読出し。

書込は POST /imports/prior-year-wip (Excel取込) 経由のみ。
ここでは一覧/単件取得とサマリのみ提供する。
"""

import uuid

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy import func, select
from sqlalchemy.ext.asyncio import AsyncSession

from app.db.session import get_db
from app.models.cost import PriorYearWipActual
from app.schemas.prior_year_wip_actual import (
    PriorYearWipActualRead,
    PriorYearWipActualSummary,
)

router = APIRouter()


@router.get("", response_model=list[PriorYearWipActualRead])
async def list_prior_year_wip_actuals(
    fiscal_year: int | None = None,
    wip_code: str | None = None,
    nayose: str | None = None,
    db: AsyncSession = Depends(get_db),
):
    """前年実績(仕掛品)の一覧。fiscal_year / wip_code / nayose でフィルタ可能。"""
    query = select(PriorYearWipActual)
    if fiscal_year is not None:
        query = query.where(PriorYearWipActual.fiscal_year == fiscal_year)
    if wip_code:
        query = query.where(PriorYearWipActual.wip_code == wip_code)
    if nayose:
        query = query.where(PriorYearWipActual.nayose == nayose)
    query = query.order_by(
        PriorYearWipActual.fiscal_year, PriorYearWipActual.wip_code
    )
    result = await db.execute(query)
    return result.scalars().all()


@router.get("/summary/{fiscal_year}", response_model=PriorYearWipActualSummary)
async def get_summary(fiscal_year: int, db: AsyncSession = Depends(get_db)):
    """fiscal_year 単位のサマリ統計。"""
    result = await db.execute(
        select(
            func.count(PriorYearWipActual.id),
            func.coalesce(func.sum(PriorYearWipActual.material_cost), 0),
            func.coalesce(func.sum(PriorYearWipActual.labor_cost), 0),
            func.coalesce(func.sum(PriorYearWipActual.expense_cost), 0),
            func.coalesce(func.sum(PriorYearWipActual.pre_process_cost), 0),
            func.coalesce(func.sum(PriorYearWipActual.closing_cost), 0),
        ).where(PriorYearWipActual.fiscal_year == fiscal_year)
    )
    total_rows, mat_sum, labor_sum, exp_sum, pre_sum, close_sum = result.one()

    return PriorYearWipActualSummary(
        fiscal_year=fiscal_year,
        total_rows=int(total_rows or 0),
        total_material_cost=mat_sum,
        total_labor_cost=labor_sum,
        total_expense_cost=exp_sum,
        total_pre_process_cost=pre_sum,
        total_closing_cost=close_sum,
    )


@router.get("/{record_id}", response_model=PriorYearWipActualRead)
async def get_prior_year_wip_actual(
    record_id: uuid.UUID, db: AsyncSession = Depends(get_db)
):
    result = await db.execute(
        select(PriorYearWipActual).where(PriorYearWipActual.id == record_id)
    )
    record = result.scalar_one_or_none()
    if not record:
        raise HTTPException(status_code=404, detail="前年実績(仕掛品)レコードが見つかりません")
    return record
