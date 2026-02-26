"""Cost center master CRUD API."""

import uuid

from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.db.session import get_db
from app.models.master import CostCenter, CostCenterType
from app.schemas.master import CostCenterCreate, CostCenterRead, CostCenterUpdate

router = APIRouter()


@router.get("", response_model=list[CostCenterRead])
async def list_cost_centers(
    center_type: CostCenterType | None = None,
    is_active: bool | None = None,
    db: AsyncSession = Depends(get_db),
):
    query = select(CostCenter)
    if center_type:
        query = query.where(CostCenter.center_type == center_type)
    if is_active is not None:
        query = query.where(CostCenter.is_active == is_active)
    query = query.order_by(CostCenter.sort_order, CostCenter.code)
    result = await db.execute(query)
    return result.scalars().all()


@router.get("/{center_id}", response_model=CostCenterRead)
async def get_cost_center(center_id: uuid.UUID, db: AsyncSession = Depends(get_db)):
    result = await db.execute(select(CostCenter).where(CostCenter.id == center_id))
    cc = result.scalar_one_or_none()
    if not cc:
        raise HTTPException(status_code=404, detail="部門が見つかりません")
    return cc


@router.post("", response_model=CostCenterRead, status_code=201)
async def create_cost_center(data: CostCenterCreate, db: AsyncSession = Depends(get_db)):
    existing = await db.execute(select(CostCenter).where(CostCenter.code == data.code))
    if existing.scalar_one_or_none():
        raise HTTPException(status_code=409, detail=f"部門コード '{data.code}' は既に存在します")
    cc = CostCenter(**data.model_dump())
    db.add(cc)
    await db.flush()
    await db.refresh(cc)
    return cc


@router.put("/{center_id}", response_model=CostCenterRead)
async def update_cost_center(center_id: uuid.UUID, data: CostCenterUpdate, db: AsyncSession = Depends(get_db)):
    result = await db.execute(select(CostCenter).where(CostCenter.id == center_id))
    cc = result.scalar_one_or_none()
    if not cc:
        raise HTTPException(status_code=404, detail="部門が見つかりません")
    for field, value in data.model_dump(exclude_unset=True).items():
        setattr(cc, field, value)
    await db.flush()
    await db.refresh(cc)
    return cc


@router.delete("/{center_id}")
async def delete_cost_center(center_id: uuid.UUID, db: AsyncSession = Depends(get_db)):
    result = await db.execute(select(CostCenter).where(CostCenter.id == center_id))
    cc = result.scalar_one_or_none()
    if not cc:
        raise HTTPException(status_code=404, detail="部門が見つかりません")
    await db.delete(cc)
    return {"message": "削除しました"}
