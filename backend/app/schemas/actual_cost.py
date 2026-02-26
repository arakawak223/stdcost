"""Pydantic v2 schemas for actual cost data."""

import uuid
from datetime import datetime
from decimal import Decimal

from pydantic import BaseModel, ConfigDict, Field

from app.models.cost import SourceSystem


# --- ActualCost (実際原価) ---

class ActualCostBase(BaseModel):
    product_id: uuid.UUID
    cost_center_id: uuid.UUID
    period_id: uuid.UUID
    crude_product_cost: Decimal = Field(default=Decimal("0"), decimal_places=4)
    packaging_cost: Decimal = Field(default=Decimal("0"), decimal_places=4)
    labor_cost: Decimal = Field(default=Decimal("0"), decimal_places=4)
    overhead_cost: Decimal = Field(default=Decimal("0"), decimal_places=4)
    outsourcing_cost: Decimal = Field(default=Decimal("0"), decimal_places=4)
    total_cost: Decimal = Field(default=Decimal("0"), decimal_places=4)
    quantity_produced: Decimal = Field(default=Decimal("0"), decimal_places=4)
    source_system: SourceSystem = SourceSystem.manual
    notes: str | None = None


class ActualCostCreate(ActualCostBase):
    pass


class ActualCostUpdate(BaseModel):
    crude_product_cost: Decimal | None = None
    packaging_cost: Decimal | None = None
    labor_cost: Decimal | None = None
    overhead_cost: Decimal | None = None
    outsourcing_cost: Decimal | None = None
    total_cost: Decimal | None = None
    quantity_produced: Decimal | None = None
    source_system: SourceSystem | None = None
    notes: str | None = None


class ActualCostRead(ActualCostBase):
    model_config = ConfigDict(from_attributes=True)
    id: uuid.UUID
    created_at: datetime
    updated_at: datetime


# --- CrudeProductActualCost (原体実際原価) ---

class CrudeProductActualCostBase(BaseModel):
    crude_product_id: uuid.UUID
    period_id: uuid.UUID
    material_cost: Decimal = Field(default=Decimal("0"), decimal_places=4)
    labor_cost: Decimal = Field(default=Decimal("0"), decimal_places=4)
    overhead_cost: Decimal = Field(default=Decimal("0"), decimal_places=4)
    prior_process_cost: Decimal = Field(default=Decimal("0"), decimal_places=4)
    total_cost: Decimal = Field(default=Decimal("0"), decimal_places=4)
    actual_quantity: Decimal = Field(default=Decimal("0"), decimal_places=4)
    source_system: SourceSystem = SourceSystem.geneki_db
    notes: str | None = None


class CrudeProductActualCostCreate(CrudeProductActualCostBase):
    pass


class CrudeProductActualCostUpdate(BaseModel):
    material_cost: Decimal | None = None
    labor_cost: Decimal | None = None
    overhead_cost: Decimal | None = None
    prior_process_cost: Decimal | None = None
    total_cost: Decimal | None = None
    actual_quantity: Decimal | None = None
    source_system: SourceSystem | None = None
    notes: str | None = None


class CrudeProductActualCostRead(CrudeProductActualCostBase):
    model_config = ConfigDict(from_attributes=True)
    id: uuid.UUID
    created_at: datetime
    updated_at: datetime
