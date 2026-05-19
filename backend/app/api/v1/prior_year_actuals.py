"""PriorYearActual API — 昨年実績(38期)製品別SC原価の読出し。

書込は POST /imports/prior-year-actuals (Excel取込) 経由のみ。
ここでは一覧/単件取得とサマリのみ提供する。
"""

import uuid

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy import func, select
from sqlalchemy.ext.asyncio import AsyncSession

from app.db.session import get_db
from app.models.cost import PriorYearActual
from app.schemas.prior_year_actual import PriorYearActualRead, PriorYearActualSummary

router = APIRouter()


@router.get("", response_model=list[PriorYearActualRead])
async def list_prior_year_actuals(
    fiscal_year: int | None = None,
    category: str | None = None,
    product_code: str | None = None,
    db: AsyncSession = Depends(get_db),
):
    """前年実績の一覧。fiscal_year / category / product_code でフィルタ可能。"""
    query = select(PriorYearActual)
    if fiscal_year is not None:
        query = query.where(PriorYearActual.fiscal_year == fiscal_year)
    if category:
        query = query.where(PriorYearActual.category == category)
    if product_code:
        query = query.where(PriorYearActual.product_code == product_code)
    query = query.order_by(
        PriorYearActual.fiscal_year, PriorYearActual.category, PriorYearActual.product_code
    )
    result = await db.execute(query)
    return result.scalars().all()


@router.get("/summary/{fiscal_year}", response_model=PriorYearActualSummary)
async def get_summary(fiscal_year: int, db: AsyncSession = Depends(get_db)):
    """fiscal_year 単位のサマリ統計。"""
    result = await db.execute(
        select(
            func.count(PriorYearActual.id),
            func.coalesce(func.sum(PriorYearActual.cogs_cost), 0),
            func.coalesce(func.sum(PriorYearActual.manufacturing_cost), 0),
            func.coalesce(func.sum(PriorYearActual.closing_cost), 0),
        ).where(PriorYearActual.fiscal_year == fiscal_year)
    )
    total_rows, cogs_sum, manu_sum, close_sum = result.one()

    cat_res = await db.execute(
        select(PriorYearActual.category, func.count(PriorYearActual.id))
        .where(PriorYearActual.fiscal_year == fiscal_year)
        .group_by(PriorYearActual.category)
    )
    by_category = {(cat or "(none)"): n for cat, n in cat_res.all()}

    return PriorYearActualSummary(
        fiscal_year=fiscal_year,
        total_rows=int(total_rows or 0),
        total_cogs_cost=cogs_sum,
        total_manufacturing_cost=manu_sum,
        total_closing_cost=close_sum,
        by_category=by_category,
    )


@router.get("/{record_id}", response_model=PriorYearActualRead)
async def get_prior_year_actual(record_id: uuid.UUID, db: AsyncSession = Depends(get_db)):
    result = await db.execute(
        select(PriorYearActual).where(PriorYearActual.id == record_id)
    )
    record = result.scalar_one_or_none()
    if not record:
        raise HTTPException(status_code=404, detail="前年実績レコードが見つかりません")
    return record
