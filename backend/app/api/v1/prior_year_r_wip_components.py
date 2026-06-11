"""PriorYearRWipComponent API — 昨年実績(38期)R仕掛品加重平均原価の読出し。

書込は POST /imports/prior-year-r-material / /imports/prior-year-r-labor 経由のみ。
ここでは一覧/単件取得とサマリのみ提供する。
"""

import uuid

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy import func, select
from sqlalchemy.ext.asyncio import AsyncSession

from app.db.session import get_db
from app.models.cost import PriorYearRWipComponent
from app.schemas.prior_year_r_wip_component import (
    PriorYearRWipComponentRead,
    PriorYearRWipComponentSummary,
)

router = APIRouter()


@router.get("", response_model=list[PriorYearRWipComponentRead])
async def list_prior_year_r_wip_components(
    fiscal_year: int | None = None,
    r_series: str | None = None,
    cost_component: str | None = None,
    db: AsyncSession = Depends(get_db),
):
    """前年実績(R仕掛品)の一覧。fiscal_year / r_series / cost_component でフィルタ可能。"""
    query = select(PriorYearRWipComponent)
    if fiscal_year is not None:
        query = query.where(PriorYearRWipComponent.fiscal_year == fiscal_year)
    if r_series:
        query = query.where(PriorYearRWipComponent.r_series == r_series)
    if cost_component:
        query = query.where(PriorYearRWipComponent.cost_component == cost_component)
    query = query.order_by(
        PriorYearRWipComponent.fiscal_year,
        PriorYearRWipComponent.r_series,
        PriorYearRWipComponent.cost_component,
    )
    result = await db.execute(query)
    return result.scalars().all()


@router.get("/summary/{fiscal_year}", response_model=PriorYearRWipComponentSummary)
async def get_summary(fiscal_year: int, db: AsyncSession = Depends(get_db)):
    """fiscal_year 単位のサマリ統計。"""
    total_res = await db.execute(
        select(func.count(PriorYearRWipComponent.id)).where(
            PriorYearRWipComponent.fiscal_year == fiscal_year
        )
    )
    total_rows = int(total_res.scalar() or 0)

    comp_res = await db.execute(
        select(PriorYearRWipComponent.cost_component, func.count(PriorYearRWipComponent.id))
        .where(PriorYearRWipComponent.fiscal_year == fiscal_year)
        .group_by(PriorYearRWipComponent.cost_component)
    )
    by_component = {comp: n for comp, n in comp_res.all()}

    async def _amount(component: str):
        res = await db.execute(
            select(func.coalesce(func.sum(PriorYearRWipComponent.weighted_avg_amount), 0)).where(
                PriorYearRWipComponent.fiscal_year == fiscal_year,
                PriorYearRWipComponent.cost_component == component,
            )
        )
        return res.scalar()

    return PriorYearRWipComponentSummary(
        fiscal_year=fiscal_year,
        total_rows=total_rows,
        by_component=by_component,
        total_material_amount=await _amount("material"),
        total_labor_amount=await _amount("labor"),
    )


@router.get("/{record_id}", response_model=PriorYearRWipComponentRead)
async def get_prior_year_r_wip_component(
    record_id: uuid.UUID, db: AsyncSession = Depends(get_db)
):
    result = await db.execute(
        select(PriorYearRWipComponent).where(PriorYearRWipComponent.id == record_id)
    )
    record = result.scalar_one_or_none()
    if not record:
        raise HTTPException(status_code=404, detail="前年実績(R仕掛品)レコードが見つかりません")
    return record
