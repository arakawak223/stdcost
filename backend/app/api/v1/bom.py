"""BOM (Bill of Materials) CRUD API."""

import uuid

from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.db.session import get_db
from app.models.master import BomHeader, BomLine, BomType
from app.schemas.master import BomHeaderCreate, BomHeaderRead, BomHeaderUpdate

router = APIRouter()


@router.get("", response_model=list[BomHeaderRead])
async def list_bom_headers(
    product_id: uuid.UUID | None = None,
    crude_product_id: uuid.UUID | None = None,
    bom_type: BomType | None = None,
    is_active: bool | None = None,
    db: AsyncSession = Depends(get_db),
):
    query = select(BomHeader)
    if product_id:
        query = query.where(BomHeader.product_id == product_id)
    if crude_product_id:
        query = query.where(BomHeader.crude_product_id == crude_product_id)
    if bom_type:
        query = query.where(BomHeader.bom_type == bom_type)
    if is_active is not None:
        query = query.where(BomHeader.is_active == is_active)
    query = query.order_by(BomHeader.bom_type, BomHeader.effective_date.desc())
    result = await db.execute(query)
    return result.scalars().unique().all()


@router.get("/{bom_id}", response_model=BomHeaderRead)
async def get_bom_header(bom_id: uuid.UUID, db: AsyncSession = Depends(get_db)):
    result = await db.execute(select(BomHeader).where(BomHeader.id == bom_id))
    bom = result.scalar_one_or_none()
    if not bom:
        raise HTTPException(status_code=404, detail="BOMが見つかりません")
    return bom


@router.post("", response_model=BomHeaderRead, status_code=201)
async def create_bom_header(data: BomHeaderCreate, db: AsyncSession = Depends(get_db)):
    if not data.product_id and not data.crude_product_id:
        raise HTTPException(status_code=400, detail="product_id または crude_product_id のいずれかが必須です")

    header = BomHeader(
        product_id=data.product_id,
        crude_product_id=data.crude_product_id,
        bom_type=data.bom_type,
        effective_date=data.effective_date,
        version=data.version,
        yield_rate=data.yield_rate,
        is_active=data.is_active,
        notes=data.notes,
    )
    db.add(header)
    await db.flush()

    for line_data in data.lines:
        line = BomLine(
            header_id=header.id,
            **line_data.model_dump(),
        )
        db.add(line)

    await db.flush()
    await db.refresh(header)
    return header


@router.put("/{bom_id}", response_model=BomHeaderRead)
async def update_bom_header(
    bom_id: uuid.UUID, data: BomHeaderUpdate, db: AsyncSession = Depends(get_db)
):
    result = await db.execute(select(BomHeader).where(BomHeader.id == bom_id))
    header = result.scalar_one_or_none()
    if not header:
        raise HTTPException(status_code=404, detail="BOMが見つかりません")

    update_data = data.model_dump(exclude_unset=True, exclude={"lines"})
    for field, value in update_data.items():
        setattr(header, field, value)

    # Replace all lines if provided
    if data.lines is not None:
        # Delete existing lines
        for line in list(header.lines):
            await db.delete(line)
        await db.flush()

        # Add new lines
        for line_data in data.lines:
            line = BomLine(
                header_id=header.id,
                **line_data.model_dump(),
            )
            db.add(line)

    await db.flush()
    await db.refresh(header)
    return header


@router.delete("/{bom_id}")
async def delete_bom_header(bom_id: uuid.UUID, db: AsyncSession = Depends(get_db)):
    result = await db.execute(select(BomHeader).where(BomHeader.id == bom_id))
    header = result.scalar_one_or_none()
    if not header:
        raise HTTPException(status_code=404, detail="BOMが見つかりません")
    await db.delete(header)
    return {"message": "BOMを削除しました"}
