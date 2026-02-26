"""Contractor (外注先) master CRUD API."""

import uuid

from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.db.session import get_db
from app.models.master import Contractor
from app.schemas.master import ContractorCreate, ContractorRead, ContractorUpdate

router = APIRouter()


@router.get("", response_model=list[ContractorRead])
async def list_contractors(
    page: int = Query(1, ge=1),
    per_page: int = Query(50, ge=1, le=200),
    search: str | None = None,
    is_active: bool | None = None,
    db: AsyncSession = Depends(get_db),
):
    query = select(Contractor)
    if search:
        query = query.where(Contractor.name.ilike(f"%{search}%") | Contractor.code.ilike(f"%{search}%"))
    if is_active is not None:
        query = query.where(Contractor.is_active == is_active)
    query = query.order_by(Contractor.code).offset((page - 1) * per_page).limit(per_page)
    result = await db.execute(query)
    return result.scalars().all()


@router.get("/{contractor_id}", response_model=ContractorRead)
async def get_contractor(contractor_id: uuid.UUID, db: AsyncSession = Depends(get_db)):
    result = await db.execute(select(Contractor).where(Contractor.id == contractor_id))
    contractor = result.scalar_one_or_none()
    if not contractor:
        raise HTTPException(status_code=404, detail="外注先が見つかりません")
    return contractor


@router.post("", response_model=ContractorRead, status_code=201)
async def create_contractor(data: ContractorCreate, db: AsyncSession = Depends(get_db)):
    existing = await db.execute(select(Contractor).where(Contractor.code == data.code))
    if existing.scalar_one_or_none():
        raise HTTPException(status_code=409, detail=f"外注先コード '{data.code}' は既に存在します")
    contractor = Contractor(**data.model_dump())
    db.add(contractor)
    await db.flush()
    await db.refresh(contractor)
    return contractor


@router.put("/{contractor_id}", response_model=ContractorRead)
async def update_contractor(contractor_id: uuid.UUID, data: ContractorUpdate, db: AsyncSession = Depends(get_db)):
    result = await db.execute(select(Contractor).where(Contractor.id == contractor_id))
    contractor = result.scalar_one_or_none()
    if not contractor:
        raise HTTPException(status_code=404, detail="外注先が見つかりません")
    for field, value in data.model_dump(exclude_unset=True).items():
        setattr(contractor, field, value)
    await db.flush()
    await db.refresh(contractor)
    return contractor


@router.delete("/{contractor_id}")
async def delete_contractor(contractor_id: uuid.UUID, db: AsyncSession = Depends(get_db)):
    result = await db.execute(select(Contractor).where(Contractor.id == contractor_id))
    contractor = result.scalar_one_or_none()
    if not contractor:
        raise HTTPException(status_code=404, detail="外注先が見つかりません")
    await db.delete(contractor)
    return {"message": "削除しました"}
