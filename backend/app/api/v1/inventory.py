"""Inventory Movement CRUD API."""

import uuid

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.db.session import get_db
from app.models.cost import InventoryMovement, MovementType
from app.schemas.inventory import (
    InventoryMovementCreate,
    InventoryMovementRead,
    InventoryMovementUpdate,
)

router = APIRouter()


@router.get("", response_model=list[InventoryMovementRead])
async def list_inventory_movements(
    period_id: uuid.UUID | None = None,
    movement_type: MovementType | None = None,
    product_id: uuid.UUID | None = None,
    crude_product_id: uuid.UUID | None = None,
    material_id: uuid.UUID | None = None,
    db: AsyncSession = Depends(get_db),
):
    query = select(InventoryMovement)
    if period_id:
        query = query.where(InventoryMovement.period_id == period_id)
    if movement_type:
        query = query.where(InventoryMovement.movement_type == movement_type)
    if product_id:
        query = query.where(InventoryMovement.product_id == product_id)
    if crude_product_id:
        query = query.where(InventoryMovement.crude_product_id == crude_product_id)
    if material_id:
        query = query.where(InventoryMovement.material_id == material_id)
    query = query.order_by(InventoryMovement.movement_date.desc())
    result = await db.execute(query)
    return result.scalars().all()


@router.get("/{record_id}", response_model=InventoryMovementRead)
async def get_inventory_movement(
    record_id: uuid.UUID, db: AsyncSession = Depends(get_db)
):
    result = await db.execute(
        select(InventoryMovement).where(InventoryMovement.id == record_id)
    )
    record = result.scalar_one_or_none()
    if not record:
        raise HTTPException(status_code=404, detail="在庫移動が見つかりません")
    return record


@router.post("", response_model=InventoryMovementRead, status_code=201)
async def create_inventory_movement(
    data: InventoryMovementCreate, db: AsyncSession = Depends(get_db)
):
    record = InventoryMovement(**data.model_dump())
    db.add(record)
    await db.flush()
    await db.refresh(record)
    return record


@router.put("/{record_id}", response_model=InventoryMovementRead)
async def update_inventory_movement(
    record_id: uuid.UUID,
    data: InventoryMovementUpdate,
    db: AsyncSession = Depends(get_db),
):
    result = await db.execute(
        select(InventoryMovement).where(InventoryMovement.id == record_id)
    )
    record = result.scalar_one_or_none()
    if not record:
        raise HTTPException(status_code=404, detail="在庫移動が見つかりません")

    update_data = data.model_dump(exclude_unset=True)
    for field, value in update_data.items():
        setattr(record, field, value)
    await db.flush()
    await db.refresh(record)
    return record


@router.delete("/{record_id}")
async def delete_inventory_movement(
    record_id: uuid.UUID, db: AsyncSession = Depends(get_db)
):
    result = await db.execute(
        select(InventoryMovement).where(InventoryMovement.id == record_id)
    )
    record = result.scalar_one_or_none()
    if not record:
        raise HTTPException(status_code=404, detail="在庫移動が見つかりません")
    await db.delete(record)
    return {"message": "在庫移動を削除しました"}
