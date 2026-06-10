"""Pydantic schemas for PriorYearOutsourceActual (F-01 横展開: 31SC外注製品)."""

import uuid
from datetime import datetime
from decimal import Decimal

from pydantic import BaseModel, ConfigDict


class PriorYearOutsourceActualRead(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: uuid.UUID
    fiscal_year: int
    product_code: str
    product_name: str | None
    product_id: uuid.UUID | None
    section: str | None
    contractor_code: str | None
    contractor_name: str | None
    supplied_material_code: str | None
    supplied_material_label: str | None

    actual_processing_cost: Decimal
    actual_other_cost: Decimal
    actual_product_cost: Decimal
    std_processing_cost: Decimal
    std_other_cost: Decimal
    std_product_cost: Decimal

    opening_qty: Decimal
    opening_cost: Decimal
    production_qty: Decimal
    production_cost: Decimal
    sales_qty: Decimal
    sales_cost: Decimal
    closing_qty: Decimal
    closing_cost: Decimal

    movements: dict

    source_file: str | None
    source_sheet: str | None
    import_batch_id: uuid.UUID | None
    notes: str | None
    created_at: datetime
    updated_at: datetime


class PriorYearOutsourceActualSummary(BaseModel):
    """fiscal_year 単位のサマリ。"""
    fiscal_year: int
    total_rows: int
    matched_rows: int
    total_production_cost: Decimal
    total_sales_cost: Decimal
    total_closing_cost: Decimal
    by_section: dict[str, int]
