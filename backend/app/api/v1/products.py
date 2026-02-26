"""Product master CRUD API."""

import csv
import io
import uuid

from fastapi import APIRouter, Depends, HTTPException, Query, UploadFile
from sqlalchemy import func, select
from sqlalchemy.ext.asyncio import AsyncSession

from app.db.session import get_db
from app.models.master import Product, ProductType
from app.schemas.common import BulkImportResult
from app.schemas.master import ProductCreate, ProductRead, ProductUpdate

router = APIRouter()


@router.get("", response_model=list[ProductRead])
async def list_products(
    page: int = Query(1, ge=1),
    per_page: int = Query(50, ge=1, le=200),
    search: str | None = None,
    product_group: str | None = None,
    product_type: ProductType | None = None,
    is_active: bool | None = None,
    db: AsyncSession = Depends(get_db),
):
    query = select(Product)
    if search:
        query = query.where(Product.name.ilike(f"%{search}%") | Product.code.ilike(f"%{search}%"))
    if product_group:
        query = query.where(Product.product_group == product_group)
    if product_type:
        query = query.where(Product.product_type == product_type)
    if is_active is not None:
        query = query.where(Product.is_active == is_active)
    query = query.order_by(Product.code).offset((page - 1) * per_page).limit(per_page)
    result = await db.execute(query)
    return result.scalars().all()


@router.get("/count")
async def count_products(
    search: str | None = None,
    product_group: str | None = None,
    product_type: ProductType | None = None,
    is_active: bool | None = None,
    db: AsyncSession = Depends(get_db),
):
    query = select(func.count(Product.id))
    if search:
        query = query.where(Product.name.ilike(f"%{search}%") | Product.code.ilike(f"%{search}%"))
    if product_group:
        query = query.where(Product.product_group == product_group)
    if product_type:
        query = query.where(Product.product_type == product_type)
    if is_active is not None:
        query = query.where(Product.is_active == is_active)
    result = await db.execute(query)
    return {"count": result.scalar_one()}


@router.get("/groups")
async def list_product_groups(db: AsyncSession = Depends(get_db)):
    result = await db.execute(
        select(Product.product_group).where(Product.product_group.isnot(None)).distinct().order_by(Product.product_group)
    )
    return [row[0] for row in result.all()]


@router.get("/{product_id}", response_model=ProductRead)
async def get_product(product_id: uuid.UUID, db: AsyncSession = Depends(get_db)):
    result = await db.execute(select(Product).where(Product.id == product_id))
    product = result.scalar_one_or_none()
    if not product:
        raise HTTPException(status_code=404, detail="製品が見つかりません")
    return product


@router.post("", response_model=ProductRead, status_code=201)
async def create_product(data: ProductCreate, db: AsyncSession = Depends(get_db)):
    existing = await db.execute(select(Product).where(Product.code == data.code))
    if existing.scalar_one_or_none():
        raise HTTPException(status_code=409, detail=f"製品コード '{data.code}' は既に存在します")
    product = Product(**data.model_dump())
    db.add(product)
    await db.flush()
    await db.refresh(product)
    return product


@router.put("/{product_id}", response_model=ProductRead)
async def update_product(product_id: uuid.UUID, data: ProductUpdate, db: AsyncSession = Depends(get_db)):
    result = await db.execute(select(Product).where(Product.id == product_id))
    product = result.scalar_one_or_none()
    if not product:
        raise HTTPException(status_code=404, detail="製品が見つかりません")
    update_data = data.model_dump(exclude_unset=True)
    for field, value in update_data.items():
        setattr(product, field, value)
    await db.flush()
    await db.refresh(product)
    return product


@router.delete("/{product_id}")
async def delete_product(product_id: uuid.UUID, db: AsyncSession = Depends(get_db)):
    result = await db.execute(select(Product).where(Product.id == product_id))
    product = result.scalar_one_or_none()
    if not product:
        raise HTTPException(status_code=404, detail="製品が見つかりません")
    await db.delete(product)
    return {"message": "削除しました"}


@router.post("/bulk-import", response_model=BulkImportResult)
async def bulk_import_products(file: UploadFile, db: AsyncSession = Depends(get_db)):
    """CSV一括インポート。columns: code, name, name_short, product_group, unit, standard_lot_size"""
    if not file.filename or not file.filename.endswith(".csv"):
        raise HTTPException(status_code=400, detail="CSVファイルをアップロードしてください")

    content = await file.read()
    text = content.decode("utf-8-sig")
    reader = csv.DictReader(io.StringIO(text))

    created = 0
    updated = 0
    errors: list[str] = []
    total = 0

    for i, row in enumerate(reader, start=2):
        total += 1
        code = row.get("code", "").strip()
        if not code:
            errors.append(f"行{i}: コードが空です")
            continue
        name = row.get("name", "").strip()
        if not name:
            errors.append(f"行{i}: 名前が空です")
            continue

        result = await db.execute(select(Product).where(Product.code == code))
        existing = result.scalar_one_or_none()

        if existing:
            existing.name = name
            existing.name_short = row.get("name_short", "").strip() or existing.name_short
            existing.product_group = row.get("product_group", "").strip() or existing.product_group
            existing.unit = row.get("unit", "").strip() or existing.unit
            lot_size = row.get("standard_lot_size", "").strip()
            if lot_size:
                existing.standard_lot_size = lot_size
            updated += 1
        else:
            product = Product(
                code=code,
                name=name,
                name_short=row.get("name_short", "").strip() or None,
                product_group=row.get("product_group", "").strip() or None,
                unit=row.get("unit", "").strip() or "kg",
                standard_lot_size=row.get("standard_lot_size", "").strip() or 1,
            )
            db.add(product)
            created += 1

    return BulkImportResult(total=total, created=created, updated=updated, errors=errors)
