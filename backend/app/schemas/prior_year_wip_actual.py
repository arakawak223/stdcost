"""Pydantic schemas for PriorYearWipActual (F-01 横展開: 20 SC仕掛品)."""

import uuid
from datetime import datetime
from decimal import Decimal

from pydantic import BaseModel, ConfigDict


class PriorYearWipActualRead(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: uuid.UUID
    fiscal_year: int
    wip_code: str
    production_year: str | None
    batch_no: str | None
    nayose: str | None
    sc_unit_price: Decimal

    opening_qty: Decimal
    opening_cost: Decimal

    material_qty: Decimal
    material_cost: Decimal

    labor_qty: Decimal
    labor_cost: Decimal

    expense_qty: Decimal
    expense_cost: Decimal

    pre_process_qty: Decimal
    pre_process_cost: Decimal

    closing_qty: Decimal
    closing_cost: Decimal

    cost_items: dict

    source_file: str | None
    source_sheet: str | None
    import_batch_id: uuid.UUID | None
    notes: str | None
    created_at: datetime
    updated_at: datetime


class PriorYearWipActualSummary(BaseModel):
    """fiscal_year 単位のサマリ。"""
    fiscal_year: int
    total_rows: int
    total_material_cost: Decimal
    total_labor_cost: Decimal
    total_expense_cost: Decimal
    total_pre_process_cost: Decimal
    total_closing_cost: Decimal
