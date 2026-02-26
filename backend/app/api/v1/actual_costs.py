"""Actual Cost CRUD API."""

import uuid

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.db.session import get_db
from app.models.cost import ActualCost, CrudeProductActualCost
from app.schemas.actual_cost import (
    ActualCostCreate,
    ActualCostRead,
    ActualCostUpdate,
    CrudeProductActualCostCreate,
    CrudeProductActualCostRead,
    CrudeProductActualCostUpdate,
)

router = APIRouter()


# --- ActualCost ---

@router.get("", response_model=list[ActualCostRead])
async def list_actual_costs(
    period_id: uuid.UUID | None = None,
    product_id: uuid.UUID | None = None,
    cost_center_id: uuid.UUID | None = None,
    db: AsyncSession = Depends(get_db),
):
    query = select(ActualCost)
    if period_id:
        query = query.where(ActualCost.period_id == period_id)
    if product_id:
        query = query.where(ActualCost.product_id == product_id)
    if cost_center_id:
        query = query.where(ActualCost.cost_center_id == cost_center_id)
    query = query.order_by(ActualCost.product_id, ActualCost.cost_center_id)
    result = await db.execute(query)
    return result.scalars().all()


@router.get("/crude-products", response_model=list[CrudeProductActualCostRead])
async def list_crude_product_actual_costs(
    period_id: uuid.UUID | None = None,
    crude_product_id: uuid.UUID | None = None,
    db: AsyncSession = Depends(get_db),
):
    query = select(CrudeProductActualCost)
    if period_id:
        query = query.where(CrudeProductActualCost.period_id == period_id)
    if crude_product_id:
        query = query.where(CrudeProductActualCost.crude_product_id == crude_product_id)
    query = query.order_by(CrudeProductActualCost.crude_product_id)
    result = await db.execute(query)
    return result.scalars().all()


@router.post("/crude-products", response_model=CrudeProductActualCostRead, status_code=201)
async def create_crude_product_actual_cost(
    data: CrudeProductActualCostCreate, db: AsyncSession = Depends(get_db)
):
    existing = await db.execute(
        select(CrudeProductActualCost).where(
            CrudeProductActualCost.crude_product_id == data.crude_product_id,
            CrudeProductActualCost.period_id == data.period_id,
        )
    )
    if existing.scalar_one_or_none():
        raise HTTPException(
            status_code=409,
            detail="この原体・期間の実際原価は既に存在します",
        )

    record = CrudeProductActualCost(**data.model_dump())
    db.add(record)
    await db.flush()
    await db.refresh(record)
    return record


@router.get("/crude-products/{record_id}", response_model=CrudeProductActualCostRead)
async def get_crude_product_actual_cost(
    record_id: uuid.UUID, db: AsyncSession = Depends(get_db)
):
    result = await db.execute(
        select(CrudeProductActualCost).where(CrudeProductActualCost.id == record_id)
    )
    record = result.scalar_one_or_none()
    if not record:
        raise HTTPException(status_code=404, detail="原体実際原価が見つかりません")
    return record


@router.put("/crude-products/{record_id}", response_model=CrudeProductActualCostRead)
async def update_crude_product_actual_cost(
    record_id: uuid.UUID,
    data: CrudeProductActualCostUpdate,
    db: AsyncSession = Depends(get_db),
):
    result = await db.execute(
        select(CrudeProductActualCost).where(CrudeProductActualCost.id == record_id)
    )
    record = result.scalar_one_or_none()
    if not record:
        raise HTTPException(status_code=404, detail="原体実際原価が見つかりません")

    update_data = data.model_dump(exclude_unset=True)
    for field, value in update_data.items():
        setattr(record, field, value)
    await db.flush()
    await db.refresh(record)
    return record


@router.delete("/crude-products/{record_id}")
async def delete_crude_product_actual_cost(
    record_id: uuid.UUID, db: AsyncSession = Depends(get_db)
):
    result = await db.execute(
        select(CrudeProductActualCost).where(CrudeProductActualCost.id == record_id)
    )
    record = result.scalar_one_or_none()
    if not record:
        raise HTTPException(status_code=404, detail="原体実際原価が見つかりません")
    await db.delete(record)
    return {"message": "原体実際原価を削除しました"}


@router.get("/{record_id}", response_model=ActualCostRead)
async def get_actual_cost(record_id: uuid.UUID, db: AsyncSession = Depends(get_db)):
    result = await db.execute(select(ActualCost).where(ActualCost.id == record_id))
    record = result.scalar_one_or_none()
    if not record:
        raise HTTPException(status_code=404, detail="実際原価が見つかりません")
    return record


@router.post("", response_model=ActualCostRead, status_code=201)
async def create_actual_cost(data: ActualCostCreate, db: AsyncSession = Depends(get_db)):
    existing = await db.execute(
        select(ActualCost).where(
            ActualCost.product_id == data.product_id,
            ActualCost.cost_center_id == data.cost_center_id,
            ActualCost.period_id == data.period_id,
        )
    )
    if existing.scalar_one_or_none():
        raise HTTPException(
            status_code=409,
            detail="この製品・部門・期間の実際原価は既に存在します",
        )

    record = ActualCost(**data.model_dump())
    db.add(record)
    await db.flush()
    await db.refresh(record)
    return record


@router.put("/{record_id}", response_model=ActualCostRead)
async def update_actual_cost(
    record_id: uuid.UUID, data: ActualCostUpdate, db: AsyncSession = Depends(get_db)
):
    result = await db.execute(select(ActualCost).where(ActualCost.id == record_id))
    record = result.scalar_one_or_none()
    if not record:
        raise HTTPException(status_code=404, detail="実際原価が見つかりません")

    update_data = data.model_dump(exclude_unset=True)
    for field, value in update_data.items():
        setattr(record, field, value)
    await db.flush()
    await db.refresh(record)
    return record


@router.delete("/{record_id}")
async def delete_actual_cost(record_id: uuid.UUID, db: AsyncSession = Depends(get_db)):
    result = await db.execute(select(ActualCost).where(ActualCost.id == record_id))
    record = result.scalar_one_or_none()
    if not record:
        raise HTTPException(status_code=404, detail="実際原価が見つかりません")
    await db.delete(record)
    return {"message": "実際原価を削除しました"}
