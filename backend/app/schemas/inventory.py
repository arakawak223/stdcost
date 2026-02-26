"""Pydantic v2 schemas for inventory movement data."""

import uuid
from datetime import date, datetime
from decimal import Decimal

from pydantic import BaseModel, ConfigDict, Field

from app.models.cost import MovementType, SourceSystem


class InventoryMovementBase(BaseModel):
    product_id: uuid.UUID | None = None
    crude_product_id: uuid.UUID | None = None
    material_id: uuid.UUID | None = None
    cost_center_id: uuid.UUID
    period_id: uuid.UUID
    movement_type: MovementType
    movement_date: date
    quantity: Decimal = Field(decimal_places=4)
    unit_cost: Decimal = Field(default=Decimal("0"), decimal_places=4)
    total_cost: Decimal = Field(default=Decimal("0"), decimal_places=4)
    lot_number: str | None = None
    aging_start_date: date | None = None
    source_system: SourceSystem = SourceSystem.manual
    notes: str | None = None


class InventoryMovementCreate(InventoryMovementBase):
    pass


class InventoryMovementUpdate(BaseModel):
    product_id: uuid.UUID | None = None
    crude_product_id: uuid.UUID | None = None
    material_id: uuid.UUID | None = None
    cost_center_id: uuid.UUID | None = None
    movement_type: MovementType | None = None
    movement_date: date | None = None
    quantity: Decimal | None = None
    unit_cost: Decimal | None = None
    total_cost: Decimal | None = None
    lot_number: str | None = None
    aging_start_date: date | None = None
    source_system: SourceSystem | None = None
    notes: str | None = None


class InventoryMovementRead(InventoryMovementBase):
    model_config = ConfigDict(from_attributes=True)
    id: uuid.UUID
    created_at: datetime
    updated_at: datetime
