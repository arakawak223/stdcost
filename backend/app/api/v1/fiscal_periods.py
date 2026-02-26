"""Fiscal period CRUD API."""

import uuid

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.db.session import get_db
from app.models.master import FiscalPeriod, PeriodStatus
from app.schemas.master import FiscalPeriodCreate, FiscalPeriodRead, FiscalPeriodUpdate

router = APIRouter()


@router.get("", response_model=list[FiscalPeriodRead])
async def list_fiscal_periods(
    status: PeriodStatus | None = None,
    year: int | None = None,
    db: AsyncSession = Depends(get_db),
):
    query = select(FiscalPeriod)
    if status:
        query = query.where(FiscalPeriod.status == status)
    if year:
        query = query.where(FiscalPeriod.year == year)
    query = query.order_by(FiscalPeriod.year.desc(), FiscalPeriod.month.desc())
    result = await db.execute(query)
    return result.scalars().all()


@router.get("/{period_id}", response_model=FiscalPeriodRead)
async def get_fiscal_period(period_id: uuid.UUID, db: AsyncSession = Depends(get_db)):
    result = await db.execute(select(FiscalPeriod).where(FiscalPeriod.id == period_id))
    period = result.scalar_one_or_none()
    if not period:
        raise HTTPException(status_code=404, detail="会計期間が見つかりません")
    return period


@router.post("", response_model=FiscalPeriodRead, status_code=201)
async def create_fiscal_period(data: FiscalPeriodCreate, db: AsyncSession = Depends(get_db)):
    existing = await db.execute(
        select(FiscalPeriod).where(FiscalPeriod.year == data.year, FiscalPeriod.month == data.month)
    )
    if existing.scalar_one_or_none():
        raise HTTPException(status_code=409, detail=f"{data.year}年{data.month}月の会計期間は既に存在します")
    period = FiscalPeriod(**data.model_dump())
    db.add(period)
    await db.flush()
    await db.refresh(period)
    return period


@router.put("/{period_id}", response_model=FiscalPeriodRead)
async def update_fiscal_period(period_id: uuid.UUID, data: FiscalPeriodUpdate, db: AsyncSession = Depends(get_db)):
    result = await db.execute(select(FiscalPeriod).where(FiscalPeriod.id == period_id))
    period = result.scalar_one_or_none()
    if not period:
        raise HTTPException(status_code=404, detail="会計期間が見つかりません")
    for field, value in data.model_dump(exclude_unset=True).items():
        setattr(period, field, value)
    await db.flush()
    await db.refresh(period)
    return period
