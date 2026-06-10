"""Pydantic schemas for PriorYearMaterialActual (F-01 横展開: 10 SC原材料)."""

import uuid
from datetime import datetime
from decimal import Decimal

from pydantic import BaseModel, ConfigDict


class PriorYearMaterialActualRead(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: uuid.UUID
    fiscal_year: int
    material_code: str
    material_name: str | None
    material_id: uuid.UUID | None
    sc_unit_price: Decimal
    unit: str | None

    opening_qty: Decimal
    opening_cost: Decimal

    purchase_qty: Decimal
    purchase_cost: Decimal

    input_qty: Decimal
    input_cost: Decimal

    closing_qty: Decimal
    closing_cost: Decimal

    adjustment_items: dict

    source_file: str | None
    source_sheet: str | None
    import_batch_id: uuid.UUID | None
    notes: str | None
    created_at: datetime
    updated_at: datetime


class PriorYearMaterialActualSummary(BaseModel):
    """fiscal_year 単位のサマリ。"""
    fiscal_year: int
    total_rows: int
    matched_rows: int
    total_purchase_cost: Decimal
    total_input_cost: Decimal
    total_closing_cost: Decimal
