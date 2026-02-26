"""Pydantic v2 schemas for cost data: budgets, standard costs, calculation requests."""

import uuid
from datetime import datetime
from decimal import Decimal

from pydantic import BaseModel, ConfigDict, Field


# --- CostBudget (部門別予算) ---

class CostBudgetBase(BaseModel):
    cost_center_id: uuid.UUID
    period_id: uuid.UUID
    labor_budget: Decimal = Field(default=Decimal("0"), decimal_places=4)
    overhead_budget: Decimal = Field(default=Decimal("0"), decimal_places=4)
    outsourcing_budget: Decimal = Field(default=Decimal("0"), decimal_places=4)
    notes: str | None = None


class CostBudgetCreate(CostBudgetBase):
    pass


class CostBudgetUpdate(BaseModel):
    labor_budget: Decimal | None = None
    overhead_budget: Decimal | None = None
    outsourcing_budget: Decimal | None = None
    notes: str | None = None


class CostBudgetRead(CostBudgetBase):
    model_config = ConfigDict(from_attributes=True)
    id: uuid.UUID
    created_at: datetime
    updated_at: datetime


# --- CrudeProductStandardCost (原体標準原価) ---

class CrudeProductStandardCostRead(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    id: uuid.UUID
    crude_product_id: uuid.UUID
    period_id: uuid.UUID
    material_cost: Decimal
    labor_cost: Decimal
    overhead_cost: Decimal
    prior_process_cost: Decimal
    total_cost: Decimal
    unit_cost: Decimal
    standard_quantity: Decimal
    notes: str | None = None
    created_at: datetime
    updated_at: datetime


# --- StandardCost (製品標準原価) ---

class StandardCostRead(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    id: uuid.UUID
    product_id: uuid.UUID
    period_id: uuid.UUID
    crude_product_cost: Decimal
    packaging_cost: Decimal
    labor_cost: Decimal
    overhead_cost: Decimal
    outsourcing_cost: Decimal
    total_cost: Decimal
    unit_cost: Decimal
    lot_size: Decimal
    notes: str | None = None
    created_at: datetime
    updated_at: datetime


# --- Calculation Request/Response ---

class CalculateRequest(BaseModel):
    period_id: uuid.UUID
    product_ids: list[uuid.UUID] | None = None
    simulate: bool = False


class SimulateRequest(BaseModel):
    period_id: uuid.UUID
    overrides: dict | None = Field(default=None, description="{ material_prices?: {material_id: price}, budget_changes?: {cost_center_id: {labor_budget?, overhead_budget?}}, category_rate_changes?: {category: rate} }")


class CopyStandardCostRequest(BaseModel):
    source_period_id: uuid.UUID
    target_period_id: uuid.UUID
    overwrite: bool = False


class CopyStandardCostResponse(BaseModel):
    source_period_id: uuid.UUID
    target_period_id: uuid.UUID
    crude_product_costs_copied: int
    crude_product_costs_skipped: int
    crude_product_costs_updated: int
    product_costs_copied: int
    product_costs_skipped: int
    product_costs_updated: int


class CalculationResultSummary(BaseModel):
    period_id: uuid.UUID
    crude_products_calculated: int
    products_calculated: int
    total_crude_product_cost: Decimal
    total_product_cost: Decimal
    crude_product_costs: list[CrudeProductStandardCostRead] = []
    product_costs: list[StandardCostRead] = []
