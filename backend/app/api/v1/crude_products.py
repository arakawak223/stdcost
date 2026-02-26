"""Crude product (原体/原液) master CRUD API."""

import uuid

from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.db.session import get_db
from app.models.master import CrudeProduct, CrudeProductType
from app.schemas.master import CrudeProductCreate, CrudeProductRead, CrudeProductUpdate

router = APIRouter()


@router.get("", response_model=list[CrudeProductRead])
async def list_crude_products(
    page: int = Query(1, ge=1),
    per_page: int = Query(50, ge=1, le=200),
    search: str | None = None,
    crude_type: CrudeProductType | None = None,
    vintage_year: int | None = None,
    is_active: bool | None = None,
    db: AsyncSession = Depends(get_db),
):
    query = select(CrudeProduct)
    if search:
        query = query.where(CrudeProduct.name.ilike(f"%{search}%") | CrudeProduct.code.ilike(f"%{search}%"))
    if crude_type:
        query = query.where(CrudeProduct.crude_type == crude_type)
    if vintage_year is not None:
        query = query.where(CrudeProduct.vintage_year == vintage_year)
    if is_active is not None:
        query = query.where(CrudeProduct.is_active == is_active)
    query = query.order_by(CrudeProduct.code).offset((page - 1) * per_page).limit(per_page)
    result = await db.execute(query)
    return result.scalars().all()


@router.get("/{crude_product_id}", response_model=CrudeProductRead)
async def get_crude_product(crude_product_id: uuid.UUID, db: AsyncSession = Depends(get_db)):
    result = await db.execute(select(CrudeProduct).where(CrudeProduct.id == crude_product_id))
    crude_product = result.scalar_one_or_none()
    if not crude_product:
        raise HTTPException(status_code=404, detail="原体が見つかりません")
    return crude_product


@router.post("", response_model=CrudeProductRead, status_code=201)
async def create_crude_product(data: CrudeProductCreate, db: AsyncSession = Depends(get_db)):
    existing = await db.execute(select(CrudeProduct).where(CrudeProduct.code == data.code))
    if existing.scalar_one_or_none():
        raise HTTPException(status_code=409, detail=f"原体コード '{data.code}' は既に存在します")
    crude_product = CrudeProduct(**data.model_dump())
    db.add(crude_product)
    await db.flush()
    await db.refresh(crude_product)
    return crude_product


@router.put("/{crude_product_id}", response_model=CrudeProductRead)
async def update_crude_product(crude_product_id: uuid.UUID, data: CrudeProductUpdate, db: AsyncSession = Depends(get_db)):
    result = await db.execute(select(CrudeProduct).where(CrudeProduct.id == crude_product_id))
    crude_product = result.scalar_one_or_none()
    if not crude_product:
        raise HTTPException(status_code=404, detail="原体が見つかりません")
    for field, value in data.model_dump(exclude_unset=True).items():
        setattr(crude_product, field, value)
    await db.flush()
    await db.refresh(crude_product)
    return crude_product


@router.delete("/{crude_product_id}")
async def delete_crude_product(crude_product_id: uuid.UUID, db: AsyncSession = Depends(get_db)):
    result = await db.execute(select(CrudeProduct).where(CrudeProduct.id == crude_product_id))
    crude_product = result.scalar_one_or_none()
    if not crude_product:
        raise HTTPException(status_code=404, detail="原体が見つかりません")
    await db.delete(crude_product)
    return {"message": "削除しました"}
