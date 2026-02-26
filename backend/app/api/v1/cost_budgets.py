"""Cost Budget CRUD API."""

import uuid

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.db.session import get_db
from app.models.master import CostBudget
from app.schemas.cost import CostBudgetCreate, CostBudgetRead, CostBudgetUpdate

router = APIRouter()


@router.get("", response_model=list[CostBudgetRead])
async def list_cost_budgets(
    cost_center_id: uuid.UUID | None = None,
    period_id: uuid.UUID | None = None,
    db: AsyncSession = Depends(get_db),
):
    query = select(CostBudget)
    if cost_center_id:
        query = query.where(CostBudget.cost_center_id == cost_center_id)
    if period_id:
        query = query.where(CostBudget.period_id == period_id)
    query = query.order_by(CostBudget.cost_center_id, CostBudget.period_id)
    result = await db.execute(query)
    return result.scalars().all()


@router.get("/{budget_id}", response_model=CostBudgetRead)
async def get_cost_budget(budget_id: uuid.UUID, db: AsyncSession = Depends(get_db)):
    result = await db.execute(select(CostBudget).where(CostBudget.id == budget_id))
    budget = result.scalar_one_or_none()
    if not budget:
        raise HTTPException(status_code=404, detail="予算が見つかりません")
    return budget


@router.post("", response_model=CostBudgetRead, status_code=201)
async def create_cost_budget(data: CostBudgetCreate, db: AsyncSession = Depends(get_db)):
    # Check for duplicate
    existing = await db.execute(
        select(CostBudget).where(
            CostBudget.cost_center_id == data.cost_center_id,
            CostBudget.period_id == data.period_id,
        )
    )
    if existing.scalar_one_or_none():
        raise HTTPException(
            status_code=409,
            detail="この部門・期間の予算は既に存在します"
        )

    budget = CostBudget(**data.model_dump())
    db.add(budget)
    await db.flush()
    await db.refresh(budget)
    return budget


@router.put("/{budget_id}", response_model=CostBudgetRead)
async def update_cost_budget(
    budget_id: uuid.UUID, data: CostBudgetUpdate, db: AsyncSession = Depends(get_db)
):
    result = await db.execute(select(CostBudget).where(CostBudget.id == budget_id))
    budget = result.scalar_one_or_none()
    if not budget:
        raise HTTPException(status_code=404, detail="予算が見つかりません")

    update_data = data.model_dump(exclude_unset=True)
    for field, value in update_data.items():
        setattr(budget, field, value)
    await db.flush()
    await db.refresh(budget)
    return budget


@router.delete("/{budget_id}")
async def delete_cost_budget(budget_id: uuid.UUID, db: AsyncSession = Depends(get_db)):
    result = await db.execute(select(CostBudget).where(CostBudget.id == budget_id))
    budget = result.scalar_one_or_none()
    if not budget:
        raise HTTPException(status_code=404, detail="予算が見つかりません")
    await db.delete(budget)
    return {"message": "予算を削除しました"}
