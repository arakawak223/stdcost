"""Standard cost calculation and retrieval API."""

import uuid

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.db.session import get_db
from app.models.cost import CrudeProductStandardCost, StandardCost
from app.schemas.cost import (
    CalculateRequest,
    CalculationResultSummary,
    CopyStandardCostRequest,
    CopyStandardCostResponse,
    CrudeProductStandardCostRead,
    SimulateRequest,
    StandardCostRead,
)
from app.services.cost_calculation import calculate_standard_costs, copy_standard_costs

router = APIRouter()


@router.post("/calculate", response_model=CalculationResultSummary)
async def calculate(data: CalculateRequest, db: AsyncSession = Depends(get_db)):
    """Execute standard cost calculation for a given period."""
    result = await calculate_standard_costs(
        db=db,
        period_id=data.period_id,
        product_ids=data.product_ids,
        simulate=data.simulate,
    )
    return result


@router.post("/simulate", response_model=CalculationResultSummary)
async def simulate(data: SimulateRequest, db: AsyncSession = Depends(get_db)):
    """Simulate standard cost calculation without saving to DB."""
    result = await calculate_standard_costs(
        db=db,
        period_id=data.period_id,
        simulate=True,
        overrides=data.overrides,
    )
    return result


@router.get("", response_model=list[StandardCostRead])
async def list_standard_costs(
    period_id: uuid.UUID | None = None,
    product_id: uuid.UUID | None = None,
    db: AsyncSession = Depends(get_db),
):
    query = select(StandardCost)
    if period_id:
        query = query.where(StandardCost.period_id == period_id)
    if product_id:
        query = query.where(StandardCost.product_id == product_id)
    query = query.order_by(StandardCost.product_id)
    result = await db.execute(query)
    return result.scalars().all()


@router.get("/crude-products", response_model=list[CrudeProductStandardCostRead])
async def list_crude_product_standard_costs(
    period_id: uuid.UUID | None = None,
    crude_product_id: uuid.UUID | None = None,
    db: AsyncSession = Depends(get_db),
):
    query = select(CrudeProductStandardCost)
    if period_id:
        query = query.where(CrudeProductStandardCost.period_id == period_id)
    if crude_product_id:
        query = query.where(CrudeProductStandardCost.crude_product_id == crude_product_id)
    query = query.order_by(CrudeProductStandardCost.crude_product_id)
    result = await db.execute(query)
    return result.scalars().all()


@router.post("/copy", response_model=CopyStandardCostResponse)
async def copy_costs(data: CopyStandardCostRequest, db: AsyncSession = Depends(get_db)):
    """Copy standard costs from source period to target period."""
    try:
        result = await copy_standard_costs(
            db=db,
            source_period_id=data.source_period_id,
            target_period_id=data.target_period_id,
            overwrite=data.overwrite,
        )
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    return result


@router.get("/{cost_id}", response_model=StandardCostRead)
async def get_standard_cost(cost_id: uuid.UUID, db: AsyncSession = Depends(get_db)):
    result = await db.execute(select(StandardCost).where(StandardCost.id == cost_id))
    cost = result.scalar_one_or_none()
    if not cost:
        raise HTTPException(status_code=404, detail="標準原価が見つかりません")
    return cost
