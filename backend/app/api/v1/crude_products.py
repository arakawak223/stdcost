"""Crude product (原体/原液) master CRUD API."""

import uuid
from decimal import Decimal

from fastapi import APIRouter, Depends, HTTPException, Query
from pydantic import BaseModel
from sqlalchemy import func, select
from sqlalchemy.ext.asyncio import AsyncSession

from app.db.session import get_db
from app.models.cost import CrudeProductStandardCost
from app.models.master import CrudeProduct, CrudeProductType
from app.schemas.master import CrudeProductCreate, CrudeProductRead, CrudeProductUpdate

router = APIRouter()


class ConsolidationGroup(BaseModel):
    """名寄せキー単位の集計行"""
    sc_consolidation_key: str | None
    item_count: int
    unit_cost_min: Decimal | None
    unit_cost_max: Decimal | None
    unit_cost_avg: Decimal | None
    sample_codes: list[str]  # 先頭10件のコード(プレビュー用)


@router.get("", response_model=list[CrudeProductRead])
async def list_crude_products(
    page: int = Query(1, ge=1),
    per_page: int = Query(50, ge=1, le=2000),
    search: str | None = None,
    crude_type: CrudeProductType | None = None,
    sc_consolidation_key: str | None = None,
    vintage_year: int | None = None,
    is_active: bool | None = None,
    db: AsyncSession = Depends(get_db),
):
    query = select(CrudeProduct)
    if search:
        query = query.where(CrudeProduct.name.ilike(f"%{search}%") | CrudeProduct.code.ilike(f"%{search}%"))
    if crude_type:
        query = query.where(CrudeProduct.crude_type == crude_type)
    if sc_consolidation_key:
        query = query.where(CrudeProduct.sc_consolidation_key == sc_consolidation_key)
    if vintage_year is not None:
        query = query.where(CrudeProduct.vintage_year == vintage_year)
    if is_active is not None:
        query = query.where(CrudeProduct.is_active == is_active)
    query = query.order_by(CrudeProduct.code).offset((page - 1) * per_page).limit(per_page)
    result = await db.execute(query)
    return result.scalars().all()


@router.get("/consolidation/summary", response_model=list[ConsolidationGroup])
async def consolidation_summary(
    period_id: uuid.UUID | None = Query(None, description="指定期のSC単価を集計対象に。未指定なら最新期。"),
    db: AsyncSession = Depends(get_db),
):
    """原体マスタを sc_consolidation_key で名寄せ集計。
    各名寄キーごとの件数とSC単価(min/max/avg)、先頭10件のコードを返す。
    """
    # 1) 名寄キー単位の件数 + 先頭コードサンプル
    rows_result = await db.execute(
        select(CrudeProduct.sc_consolidation_key, CrudeProduct.code)
        .order_by(CrudeProduct.sc_consolidation_key, CrudeProduct.code)
    )
    rows = rows_result.all()
    by_key: dict[str | None, list[str]] = {}
    for key, code in rows:
        by_key.setdefault(key, []).append(code)

    # 2) 同一キー内のSC単価分布
    sc_query = (
        select(
            CrudeProduct.sc_consolidation_key,
            func.min(CrudeProductStandardCost.unit_cost),
            func.max(CrudeProductStandardCost.unit_cost),
            func.avg(CrudeProductStandardCost.unit_cost),
        )
        .join(
            CrudeProductStandardCost,
            CrudeProductStandardCost.crude_product_id == CrudeProduct.id,
        )
        .where(CrudeProductStandardCost.unit_cost > 0)
        .group_by(CrudeProduct.sc_consolidation_key)
    )
    if period_id:
        sc_query = sc_query.where(CrudeProductStandardCost.period_id == period_id)
    sc_result = await db.execute(sc_query)
    sc_map: dict[str | None, tuple[Decimal | None, Decimal | None, Decimal | None]] = {
        key: (mn, mx, avg) for key, mn, mx, avg in sc_result.all()
    }

    # 3) 統合
    groups: list[ConsolidationGroup] = []
    for key in sorted(by_key.keys(), key=lambda x: (x is None, x or "")):
        codes = by_key[key]
        mn, mx, avg = sc_map.get(key, (None, None, None))
        groups.append(ConsolidationGroup(
            sc_consolidation_key=key,
            item_count=len(codes),
            unit_cost_min=mn,
            unit_cost_max=mx,
            unit_cost_avg=avg,
            sample_codes=codes[:10],
        ))
    return groups


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
