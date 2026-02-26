"""Material master CRUD API."""

import uuid

from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.db.session import get_db
from app.models.master import Material, MaterialCategory, MaterialType
from app.schemas.master import MaterialCreate, MaterialRead, MaterialUpdate

router = APIRouter()


@router.get("", response_model=list[MaterialRead])
async def list_materials(
    page: int = Query(1, ge=1),
    per_page: int = Query(50, ge=1, le=200),
    search: str | None = None,
    material_type: MaterialType | None = None,
    category: MaterialCategory | None = None,
    is_active: bool | None = None,
    db: AsyncSession = Depends(get_db),
):
    query = select(Material)
    if search:
        query = query.where(Material.name.ilike(f"%{search}%") | Material.code.ilike(f"%{search}%"))
    if material_type:
        query = query.where(Material.material_type == material_type)
    if category:
        query = query.where(Material.category == category)
    if is_active is not None:
        query = query.where(Material.is_active == is_active)
    query = query.order_by(Material.code).offset((page - 1) * per_page).limit(per_page)
    result = await db.execute(query)
    return result.scalars().all()


@router.get("/{material_id}", response_model=MaterialRead)
async def get_material(material_id: uuid.UUID, db: AsyncSession = Depends(get_db)):
    result = await db.execute(select(Material).where(Material.id == material_id))
    material = result.scalar_one_or_none()
    if not material:
        raise HTTPException(status_code=404, detail="原材料が見つかりません")
    return material


@router.post("", response_model=MaterialRead, status_code=201)
async def create_material(data: MaterialCreate, db: AsyncSession = Depends(get_db)):
    existing = await db.execute(select(Material).where(Material.code == data.code))
    if existing.scalar_one_or_none():
        raise HTTPException(status_code=409, detail=f"原材料コード '{data.code}' は既に存在します")
    material = Material(**data.model_dump())
    db.add(material)
    await db.flush()
    await db.refresh(material)
    return material


@router.put("/{material_id}", response_model=MaterialRead)
async def update_material(material_id: uuid.UUID, data: MaterialUpdate, db: AsyncSession = Depends(get_db)):
    result = await db.execute(select(Material).where(Material.id == material_id))
    material = result.scalar_one_or_none()
    if not material:
        raise HTTPException(status_code=404, detail="原材料が見つかりません")
    for field, value in data.model_dump(exclude_unset=True).items():
        setattr(material, field, value)
    await db.flush()
    await db.refresh(material)
    return material


@router.delete("/{material_id}")
async def delete_material(material_id: uuid.UUID, db: AsyncSession = Depends(get_db)):
    result = await db.execute(select(Material).where(Material.id == material_id))
    material = result.scalar_one_or_none()
    if not material:
        raise HTTPException(status_code=404, detail="原材料が見つかりません")
    await db.delete(material)
    return {"message": "削除しました"}
