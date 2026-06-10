"""PriorYearOutsourceActual API — 昨年実績(38期)外注製品別SC原価の読出し。

書込は POST /imports/prior-year-outsource (Excel取込) 経由のみ。
ここでは一覧/単件取得とサマリのみ提供する。
"""

import uuid

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy import func, select
from sqlalchemy.ext.asyncio import AsyncSession

from app.db.session import get_db
from app.models.cost import PriorYearOutsourceActual
from app.schemas.prior_year_outsource_actual import (
    PriorYearOutsourceActualRead,
    PriorYearOutsourceActualSummary,
)

router = APIRouter()


@router.get("", response_model=list[PriorYearOutsourceActualRead])
async def list_prior_year_outsource_actuals(
    fiscal_year: int | None = None,
    section: str | None = None,
    product_code: str | None = None,
    db: AsyncSession = Depends(get_db),
):
    """前年実績(外注製品)の一覧。fiscal_year / section / product_code でフィルタ可能。"""
    query = select(PriorYearOutsourceActual)
    if fiscal_year is not None:
        query = query.where(PriorYearOutsourceActual.fiscal_year == fiscal_year)
    if section:
        query = query.where(PriorYearOutsourceActual.section == section)
    if product_code:
        query = query.where(PriorYearOutsourceActual.product_code == product_code)
    query = query.order_by(
        PriorYearOutsourceActual.fiscal_year, PriorYearOutsourceActual.product_code
    )
    result = await db.execute(query)
    return result.scalars().all()


@router.get("/summary/{fiscal_year}", response_model=PriorYearOutsourceActualSummary)
async def get_summary(fiscal_year: int, db: AsyncSession = Depends(get_db)):
    """fiscal_year 単位のサマリ統計。"""
    result = await db.execute(
        select(
            func.count(PriorYearOutsourceActual.id),
            func.count(PriorYearOutsourceActual.product_id),
            func.coalesce(func.sum(PriorYearOutsourceActual.production_cost), 0),
            func.coalesce(func.sum(PriorYearOutsourceActual.sales_cost), 0),
            func.coalesce(func.sum(PriorYearOutsourceActual.closing_cost), 0),
        ).where(PriorYearOutsourceActual.fiscal_year == fiscal_year)
    )
    total_rows, matched_rows, prod_sum, sales_sum, close_sum = result.one()

    sec_res = await db.execute(
        select(PriorYearOutsourceActual.section, func.count(PriorYearOutsourceActual.id))
        .where(PriorYearOutsourceActual.fiscal_year == fiscal_year)
        .group_by(PriorYearOutsourceActual.section)
    )
    by_section = {(sec or "(none)"): n for sec, n in sec_res.all()}

    return PriorYearOutsourceActualSummary(
        fiscal_year=fiscal_year,
        total_rows=int(total_rows or 0),
        matched_rows=int(matched_rows or 0),
        total_production_cost=prod_sum,
        total_sales_cost=sales_sum,
        total_closing_cost=close_sum,
        by_section=by_section,
    )


@router.get("/{record_id}", response_model=PriorYearOutsourceActualRead)
async def get_prior_year_outsource_actual(
    record_id: uuid.UUID, db: AsyncSession = Depends(get_db)
):
    result = await db.execute(
        select(PriorYearOutsourceActual).where(PriorYearOutsourceActual.id == record_id)
    )
    record = result.scalar_one_or_none()
    if not record:
        raise HTTPException(status_code=404, detail="前年実績(外注製品)レコードが見つかりません")
    return record
