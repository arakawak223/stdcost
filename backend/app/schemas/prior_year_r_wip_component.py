"""Pydantic schemas for PriorYearRWipComponent (F-01 横展開: 21-1/21-2 R仕掛品)."""

import uuid
from datetime import datetime
from decimal import Decimal

from pydantic import BaseModel, ConfigDict


class PriorYearRWipComponentRead(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: uuid.UUID
    fiscal_year: int
    r_series: str
    cost_component: str
    weighted_avg_qty: Decimal
    weighted_avg_amount: Decimal
    weighted_avg_unit_price: Decimal
    source_file: str | None
    source_sheet: str | None
    import_batch_id: uuid.UUID | None
    notes: str | None
    created_at: datetime
    updated_at: datetime


class PriorYearRWipComponentSummary(BaseModel):
    """fiscal_year 単位のサマリ。"""
    fiscal_year: int
    total_rows: int
    by_component: dict[str, int]
    total_material_amount: Decimal
    total_labor_amount: Decimal
