"""Pydantic schemas for PriorYearActual (F-01 昨年実績)."""

import uuid
from datetime import datetime
from decimal import Decimal

from pydantic import BaseModel, ConfigDict


class PriorYearActualRead(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: uuid.UUID
    fiscal_year: int
    category: str | None
    product_code: str
    product_name: str | None
    product_id: uuid.UUID | None

    opening_qty: Decimal
    opening_unit_price: Decimal
    opening_cost: Decimal

    manufacturing_qty: Decimal
    manufacturing_unit_price: Decimal
    manufacturing_cost: Decimal

    transfer_qty: Decimal
    transfer_unit_price: Decimal
    transfer_cost: Decimal

    cogs_qty: Decimal
    cogs_unit_price: Decimal
    cogs_cost: Decimal

    outsource_supply_qty: Decimal
    outsource_supply_unit_price: Decimal
    outsource_supply_cost: Decimal

    closing_qty: Decimal
    closing_unit_price: Decimal
    closing_cost: Decimal

    transfer_items: dict

    source_file: str | None
    source_sheet: str | None
    import_batch_id: uuid.UUID | None
    notes: str | None
    created_at: datetime
    updated_at: datetime


class PriorYearActualSummary(BaseModel):
    """fiscal_year 単位のサマリ。"""
    fiscal_year: int
    total_rows: int
    total_cogs_cost: Decimal
    total_manufacturing_cost: Decimal
    total_closing_cost: Decimal
    by_category: dict[str, int]
