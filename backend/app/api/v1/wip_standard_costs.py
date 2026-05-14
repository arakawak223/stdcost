"""WipStandardCost CRUD API — 仕掛品(半製品)標準単価（期別・名寄せキー単位）。

`material_standard_costs` と同じパターンで、`(consolidation_key, period_id)` を
UNIQUE 制約とした単価マスタ。在庫評価では Product.sc_consolidation_key 経由で参照。
"""

import uuid
from decimal import Decimal

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.db.session import get_db
from app.models.cost import WipStandardCost
from app.schemas.cost import (
    WipStandardCostBulkUpsertRequest,
    WipStandardCostBulkUpsertResponse,
    WipStandardCostCreate,
    WipStandardCostRead,
    WipStandardCostUpdate,
)

router = APIRouter()


@router.get("", response_model=list[WipStandardCostRead])
async def list_wip_standard_costs(
    consolidation_key: str | None = None,
    period_id: uuid.UUID | None = None,
    db: AsyncSession = Depends(get_db),
):
    """仕掛品標準単価の一覧。consolidation_key / period_id でフィルタ可能。"""
    query = select(WipStandardCost)
    if consolidation_key:
        query = query.where(WipStandardCost.consolidation_key == consolidation_key)
    if period_id:
        query = query.where(WipStandardCost.period_id == period_id)
    query = query.order_by(
        WipStandardCost.period_id, WipStandardCost.consolidation_key
    )
    result = await db.execute(query)
    return result.scalars().all()


@router.get("/{record_id}", response_model=WipStandardCostRead)
async def get_wip_standard_cost(
    record_id: uuid.UUID, db: AsyncSession = Depends(get_db)
):
    result = await db.execute(
        select(WipStandardCost).where(WipStandardCost.id == record_id)
    )
    record = result.scalar_one_or_none()
    if not record:
        raise HTTPException(status_code=404, detail="仕掛品標準単価が見つかりません")
    return record


@router.post("", response_model=WipStandardCostRead, status_code=201)
async def create_wip_standard_cost(
    data: WipStandardCostCreate, db: AsyncSession = Depends(get_db)
):
    existing = await db.execute(
        select(WipStandardCost).where(
            WipStandardCost.consolidation_key == data.consolidation_key,
            WipStandardCost.period_id == data.period_id,
        )
    )
    if existing.scalar_one_or_none():
        raise HTTPException(
            status_code=409,
            detail="この名寄せキー・期間の標準単価は既に存在します（PUT で更新してください）",
        )
    record = WipStandardCost(**data.model_dump())
    db.add(record)
    await db.flush()
    await db.refresh(record)
    return record


@router.put("/{record_id}", response_model=WipStandardCostRead)
async def update_wip_standard_cost(
    record_id: uuid.UUID,
    data: WipStandardCostUpdate,
    db: AsyncSession = Depends(get_db),
):
    result = await db.execute(
        select(WipStandardCost).where(WipStandardCost.id == record_id)
    )
    record = result.scalar_one_or_none()
    if not record:
        raise HTTPException(status_code=404, detail="仕掛品標準単価が見つかりません")
    update_data = data.model_dump(exclude_unset=True)
    for field, value in update_data.items():
        setattr(record, field, value)
    await db.flush()
    await db.refresh(record)
    return record


@router.delete("/{record_id}")
async def delete_wip_standard_cost(
    record_id: uuid.UUID, db: AsyncSession = Depends(get_db)
):
    result = await db.execute(
        select(WipStandardCost).where(WipStandardCost.id == record_id)
    )
    record = result.scalar_one_or_none()
    if not record:
        raise HTTPException(status_code=404, detail="仕掛品標準単価が見つかりません")
    await db.delete(record)
    return {"message": "仕掛品標準単価を削除しました"}


@router.post("/bulk-upsert", response_model=WipStandardCostBulkUpsertResponse)
async def bulk_upsert_wip_standard_costs(
    data: WipStandardCostBulkUpsertRequest,
    db: AsyncSession = Depends(get_db),
):
    """指定期間で複数の仕掛品単価を一括 INSERT / UPDATE する。

    Excel 取込で同一期間に多数のキー別単価をまとめて反映する用途。
    既存レコードは unit_cost / 内訳4列 / effective_date / notes を上書きし、
    値に差分がない場合は unchanged にカウント。
    """
    existing_result = await db.execute(
        select(WipStandardCost).where(
            WipStandardCost.period_id == data.period_id
        )
    )
    existing_map: dict[str, WipStandardCost] = {
        r.consolidation_key: r for r in existing_result.scalars().all()
    }

    inserted = 0
    updated = 0
    unchanged = 0
    breakdown_fields = ("pre_process_cost", "material_cost", "labor_cost", "expense_cost")
    for item in data.items:
        existing = existing_map.get(item.consolidation_key)
        new_cost = Decimal(str(item.unit_cost))
        if existing is None:
            db.add(
                WipStandardCost(
                    consolidation_key=item.consolidation_key,
                    period_id=data.period_id,
                    unit_cost=new_cost,
                    pre_process_cost=Decimal(str(item.pre_process_cost)),
                    material_cost=Decimal(str(item.material_cost)),
                    labor_cost=Decimal(str(item.labor_cost)),
                    expense_cost=Decimal(str(item.expense_cost)),
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
            for field in breakdown_fields:
                new_val = Decimal(str(getattr(item, field)))
                if Decimal(str(getattr(existing, field))) != new_val:
                    setattr(existing, field, new_val)
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
    return WipStandardCostBulkUpsertResponse(
        period_id=data.period_id,
        inserted=inserted,
        updated=updated,
        unchanged=unchanged,
    )
