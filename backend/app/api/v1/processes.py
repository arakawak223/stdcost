"""Process (工程) master CRUD API."""

import uuid

from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.db.session import get_db
from app.models.master import Process
from app.schemas.master import ProcessCreate, ProcessRead, ProcessUpdate

router = APIRouter()


@router.get("", response_model=list[ProcessRead])
async def list_processes(
    page: int = Query(1, ge=1),
    per_page: int = Query(50, ge=1, le=2000),
    search: str | None = None,
    is_active: bool | None = None,
    db: AsyncSession = Depends(get_db),
):
    query = select(Process)
    if search:
        query = query.where(Process.name.ilike(f"%{search}%") | Process.code.ilike(f"%{search}%"))
    if is_active is not None:
        query = query.where(Process.is_active == is_active)
    query = query.order_by(Process.sort_order, Process.code).offset((page - 1) * per_page).limit(per_page)
    result = await db.execute(query)
    return result.scalars().all()


@router.get("/{process_id}", response_model=ProcessRead)
async def get_process(process_id: uuid.UUID, db: AsyncSession = Depends(get_db)):
    result = await db.execute(select(Process).where(Process.id == process_id))
    process = result.scalar_one_or_none()
    if not process:
        raise HTTPException(status_code=404, detail="工程が見つかりません")
    return process


@router.post("", response_model=ProcessRead, status_code=201)
async def create_process(data: ProcessCreate, db: AsyncSession = Depends(get_db)):
    existing = await db.execute(select(Process).where(Process.code == data.code))
    if existing.scalar_one_or_none():
        raise HTTPException(status_code=409, detail=f"工程コード '{data.code}' は既に存在します")
    process = Process(**data.model_dump())
    db.add(process)
    await db.flush()
    await db.refresh(process)
    return process


@router.put("/{process_id}", response_model=ProcessRead)
async def update_process(process_id: uuid.UUID, data: ProcessUpdate, db: AsyncSession = Depends(get_db)):
    result = await db.execute(select(Process).where(Process.id == process_id))
    process = result.scalar_one_or_none()
    if not process:
        raise HTTPException(status_code=404, detail="工程が見つかりません")
    for field, value in data.model_dump(exclude_unset=True).items():
        setattr(process, field, value)
    await db.flush()
    await db.refresh(process)
    return process


@router.delete("/{process_id}")
async def delete_process(process_id: uuid.UUID, db: AsyncSession = Depends(get_db)):
    result = await db.execute(select(Process).where(Process.id == process_id))
    process = result.scalar_one_or_none()
    if not process:
        raise HTTPException(status_code=404, detail="工程が見つかりません")
    await db.delete(process)
    return {"message": "削除しました"}
