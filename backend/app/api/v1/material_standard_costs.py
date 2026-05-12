"""MaterialStandardCost CRUD API — 原材料標準単価（期別）。

期別の単価履歴を保持し、在庫評価・原価計算で参照される。
書込時は (material_id, period_id) で UNIQUE 制約。bulk-upsert は同 period_id
配下を一括 INSERT/UPDATE する。
"""

import uuid
from decimal import Decimal

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.db.session import get_db
from app.models.cost import MaterialStandardCost
from app.schemas.cost import (
    MaterialStandardCostBulkUpsertRequest,
    MaterialStandardCostBulkUpsertResponse,
    MaterialStandardCostCreate,
    MaterialStandardCostRead,
    MaterialStandardCostUpdate,
)

router = APIRouter()


@router.get("", response_model=list[MaterialStandardCostRead])
async def list_material_standard_costs(
    material_id: uuid.UUID | None = None,
    period_id: uuid.UUID | None = None,
    db: AsyncSession = Depends(get_db),
):
    """原材料標準単価の一覧。material_id / period_id でフィルタ可能。"""
    query = select(MaterialStandardCost)
    if material_id:
        query = query.where(MaterialStandardCost.material_id == material_id)
    if period_id:
        query = query.where(MaterialStandardCost.period_id == period_id)
    query = query.order_by(
        MaterialStandardCost.period_id, MaterialStandardCost.material_id
    )
    result = await db.execute(query)
    return result.scalars().all()


@router.get("/{record_id}", response_model=MaterialStandardCostRead)
async def get_material_standard_cost(
    record_id: uuid.UUID, db: AsyncSession = Depends(get_db)
):
    result = await db.execute(
        select(MaterialStandardCost).where(MaterialStandardCost.id == record_id)
    )
    record = result.scalar_one_or_none()
    if not record:
        raise HTTPException(status_code=404, detail="原材料標準単価が見つかりません")
    return record


@router.post("", response_model=MaterialStandardCostRead, status_code=201)
async def create_material_standard_cost(
    data: MaterialStandardCostCreate, db: AsyncSession = Depends(get_db)
):
    # (material_id, period_id) で重複チェック
    existing = await db.execute(
        select(MaterialStandardCost).where(
            MaterialStandardCost.material_id == data.material_id,
            MaterialStandardCost.period_id == data.period_id,
        )
    )
    if existing.scalar_one_or_none():
        raise HTTPException(
            status_code=409,
            detail="この原材料・期間の標準単価は既に存在します（PUT で更新してください）",
        )
    record = MaterialStandardCost(**data.model_dump())
    db.add(record)
    await db.flush()
    await db.refresh(record)
    return record


@router.put("/{record_id}", response_model=MaterialStandardCostRead)
async def update_material_standard_cost(
    record_id: uuid.UUID,
    data: MaterialStandardCostUpdate,
    db: AsyncSession = Depends(get_db),
):
    result = await db.execute(
        select(MaterialStandardCost).where(MaterialStandardCost.id == record_id)
    )
    record = result.scalar_one_or_none()
    if not record:
        raise HTTPException(status_code=404, detail="原材料標準単価が見つかりません")
    update_data = data.model_dump(exclude_unset=True)
    for field, value in update_data.items():
        setattr(record, field, value)
    await db.flush()
    await db.refresh(record)
    return record


@router.delete("/{record_id}")
async def delete_material_standard_cost(
    record_id: uuid.UUID, db: AsyncSession = Depends(get_db)
):
    result = await db.execute(
        select(MaterialStandardCost).where(MaterialStandardCost.id == record_id)
    )
    record = result.scalar_one_or_none()
    if not record:
        raise HTTPException(status_code=404, detail="原材料標準単価が見つかりません")
    await db.delete(record)
    return {"message": "原材料標準単価を削除しました"}


@router.post("/bulk-upsert", response_model=MaterialStandardCostBulkUpsertResponse)
async def bulk_upsert_material_standard_costs(
    data: MaterialStandardCostBulkUpsertRequest,
    db: AsyncSession = Depends(get_db),
):
    """指定期間で複数の原材料単価を一括 INSERT / UPDATE する。

    SC ファイル取込で同一期間に多数の単価をまとめて反映する用途。
    既存レコードは unit_cost / effective_date / notes を上書き、
    値に差分がない場合は unchanged にカウント。
    """
    # 既存レコードを引いて map 化
    existing_result = await db.execute(
        select(MaterialStandardCost).where(
            MaterialStandardCost.period_id == data.period_id
        )
    )
    existing_map: dict[uuid.UUID, MaterialStandardCost] = {
        r.material_id: r for r in existing_result.scalars().all()
    }

    inserted = 0
    updated = 0
    unchanged = 0
    for item in data.items:
        existing = existing_map.get(item.material_id)
        new_cost = Decimal(str(item.unit_cost))
        if existing is None:
            db.add(
                MaterialStandardCost(
                    material_id=item.material_id,
                    period_id=data.period_id,
                    unit_cost=new_cost,
                    effective_date=item.effective_date,
                    notes=item.notes,
                )
            )
            inserted += 1
        else:
            changed = False
            if Decimal(str(existing.unit_cost)) != new_cost:
                existing.unit_cost = new_cost
                changed = True
            if item.effective_date is not None and existing.effective_date != item.effective_date:
                existing.effective_date = item.effective_date
                changed = True
            if item.notes is not None and existing.notes != item.notes:
                existing.notes = item.notes
                changed = True
            if changed:
                updated += 1
            else:
                unchanged += 1

    await db.flush()
    return MaterialStandardCostBulkUpsertResponse(
        period_id=data.period_id,
        inserted=inserted,
        updated=updated,
        unchanged=unchanged,
    )
