"""Allocation Rules CRUD API."""

import uuid

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.db.session import get_db
from app.models.master import AllocationRule, AllocationRuleTarget
from app.schemas.master import AllocationRuleCreate, AllocationRuleRead, AllocationRuleUpdate

router = APIRouter()


@router.get("", response_model=list[AllocationRuleRead])
async def list_allocation_rules(
    is_active: bool | None = None,
    db: AsyncSession = Depends(get_db),
):
    query = select(AllocationRule)
    if is_active is not None:
        query = query.where(AllocationRule.is_active == is_active)
    query = query.order_by(AllocationRule.name)
    result = await db.execute(query)
    return result.scalars().unique().all()


@router.get("/{rule_id}", response_model=AllocationRuleRead)
async def get_allocation_rule(rule_id: uuid.UUID, db: AsyncSession = Depends(get_db)):
    result = await db.execute(select(AllocationRule).where(AllocationRule.id == rule_id))
    rule = result.scalar_one_or_none()
    if not rule:
        raise HTTPException(status_code=404, detail="配賦ルールが見つかりません")
    return rule


@router.post("", response_model=AllocationRuleRead, status_code=201)
async def create_allocation_rule(data: AllocationRuleCreate, db: AsyncSession = Depends(get_db)):
    rule = AllocationRule(
        name=data.name,
        source_cost_center_id=data.source_cost_center_id,
        basis=data.basis,
        is_active=data.is_active,
        notes=data.notes,
    )
    db.add(rule)
    await db.flush()

    for target_data in data.targets:
        target = AllocationRuleTarget(
            rule_id=rule.id,
            target_cost_center_id=target_data.target_cost_center_id,
            ratio=target_data.ratio,
        )
        db.add(target)

    await db.flush()
    await db.refresh(rule)
    return rule


@router.put("/{rule_id}", response_model=AllocationRuleRead)
async def update_allocation_rule(
    rule_id: uuid.UUID, data: AllocationRuleUpdate, db: AsyncSession = Depends(get_db)
):
    result = await db.execute(select(AllocationRule).where(AllocationRule.id == rule_id))
    rule = result.scalar_one_or_none()
    if not rule:
        raise HTTPException(status_code=404, detail="配賦ルールが見つかりません")

    update_data = data.model_dump(exclude_unset=True, exclude={"targets"})
    for field, value in update_data.items():
        setattr(rule, field, value)

    # Replace all targets if provided
    if data.targets is not None:
        for target in list(rule.targets):
            await db.delete(target)
        await db.flush()

        for target_data in data.targets:
            target = AllocationRuleTarget(
                rule_id=rule.id,
                target_cost_center_id=target_data.target_cost_center_id,
                ratio=target_data.ratio,
            )
            db.add(target)

    await db.flush()
    await db.refresh(rule)
    return rule


@router.delete("/{rule_id}")
async def delete_allocation_rule(rule_id: uuid.UUID, db: AsyncSession = Depends(get_db)):
    result = await db.execute(select(AllocationRule).where(AllocationRule.id == rule_id))
    rule = result.scalar_one_or_none()
    if not rule:
        raise HTTPException(status_code=404, detail="配賦ルールが見つかりません")
    await db.delete(rule)
    return {"message": "配賦ルールを削除しました"}
