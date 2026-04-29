"""Inventory Valuation CRUD + 計算API。"""

import uuid

from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.db.session import get_db
from app.models.cost import InventoryCategory, InventoryValuation
from app.schemas.inventory_valuation import (
    InventoryValuationCreate,
    InventoryValuationRead,
    InventoryValuationUpdate,
    ProductInventoryFlow,
    ValuationSummary,
)
from app.services.inventory_valuation import (
    get_product_inventory_flow,
    get_valuation_summary,
    recalculate_valuation_amounts,
)

router = APIRouter()


@router.get("", response_model=list[InventoryValuationRead])
async def list_inventory_valuations(
    period_id: uuid.UUID | None = None,
    category: InventoryCategory | None = None,
    warehouse_name: str | None = None,
    item_code: str | None = None,
    limit: int = Query(default=500, le=5000),
    offset: int = 0,
    db: AsyncSession = Depends(get_db),
):
    """在庫評価レコード一覧。期間・区分・倉庫・商品コードでフィルタ可能。"""
    query = select(InventoryValuation)
    if period_id:
        query = query.where(InventoryValuation.period_id == period_id)
    if category:
        query = query.where(InventoryValuation.category == category)
    if warehouse_name:
        query = query.where(InventoryValuation.warehouse_name == warehouse_name)
    if item_code:
        query = query.where(InventoryValuation.item_code == item_code)
    query = query.order_by(
        InventoryValuation.warehouse_name, InventoryValuation.item_code
    ).limit(limit).offset(offset)
    result = await db.execute(query)
    return result.scalars().all()


@router.get("/summary", response_model=ValuationSummary)
async def get_summary(
    period_id: uuid.UUID,
    db: AsyncSession = Depends(get_db),
):
    """指定期間の在庫評価サマリ（区分別・倉庫別の集計）。"""
    return await get_valuation_summary(db, period_id)


@router.get("/product-flow", response_model=list[ProductInventoryFlow])
async def get_product_flow(
    period_id: uuid.UUID,
    prior_period_id: uuid.UUID | None = None,
    db: AsyncSession = Depends(get_db),
):
    """製品ごとの期首+受入-払出=期末の在庫推移を標準単価ベースで返す。"""
    return await get_product_inventory_flow(db, period_id, prior_period_id)


@router.post("/recalculate")
async def recalculate(
    period_id: uuid.UUID,
    db: AsyncSession = Depends(get_db),
):
    """マスタの標準単価を再取得して、評価金額を再計算する。"""
    updated = await recalculate_valuation_amounts(db, period_id)
    return {"updated": updated, "message": f"{updated}件の評価金額を再計算しました"}


@router.get("/{record_id}", response_model=InventoryValuationRead)
async def get_inventory_valuation(
    record_id: uuid.UUID, db: AsyncSession = Depends(get_db)
):
    result = await db.execute(
        select(InventoryValuation).where(InventoryValuation.id == record_id)
    )
    record = result.scalar_one_or_none()
    if not record:
        raise HTTPException(status_code=404, detail="在庫評価レコードが見つかりません")
    return record


@router.post("", response_model=InventoryValuationRead, status_code=201)
async def create_inventory_valuation(
    data: InventoryValuationCreate, db: AsyncSession = Depends(get_db)
):
    payload = data.model_dump()
    # valuation_amount が未指定なら quantity × standard_unit_price で計算
    if payload.get("valuation_amount") in (None, 0) and payload.get("quantity") and payload.get("standard_unit_price"):
        payload["valuation_amount"] = payload["quantity"] * payload["standard_unit_price"]
    record = InventoryValuation(**payload)
    db.add(record)
    await db.flush()
    await db.refresh(record)
    return record


@router.put("/{record_id}", response_model=InventoryValuationRead)
async def update_inventory_valuation(
    record_id: uuid.UUID,
    data: InventoryValuationUpdate,
    db: AsyncSession = Depends(get_db),
):
    result = await db.execute(
        select(InventoryValuation).where(InventoryValuation.id == record_id)
    )
    record = result.scalar_one_or_none()
    if not record:
        raise HTTPException(status_code=404, detail="在庫評価レコードが見つかりません")

    update_data = data.model_dump(exclude_unset=True)
    for field, value in update_data.items():
        setattr(record, field, value)
    # 数量・単価が変わった場合は金額を自動再計算
    if any(k in update_data for k in ("quantity", "standard_unit_price")) and "valuation_amount" not in update_data:
        record.valuation_amount = record.quantity * record.standard_unit_price
    await db.flush()
    await db.refresh(record)
    return record


@router.delete("/{record_id}")
async def delete_inventory_valuation(
    record_id: uuid.UUID, db: AsyncSession = Depends(get_db)
):
    result = await db.execute(
        select(InventoryValuation).where(InventoryValuation.id == record_id)
    )
    record = result.scalar_one_or_none()
    if not record:
        raise HTTPException(status_code=404, detail="在庫評価レコードが見つかりません")
    await db.delete(record)
    return {"message": "在庫評価レコードを削除しました"}
