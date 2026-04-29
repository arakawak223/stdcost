"""Pydantic v2 schemas for inventory valuation."""

import uuid
from datetime import datetime
from decimal import Decimal

from pydantic import BaseModel, ConfigDict, Field

from app.models.cost import InventoryCategory, SourceSystem


class InventoryValuationBase(BaseModel):
    period_id: uuid.UUID
    item_code: str = Field(max_length=30)
    item_name: str | None = Field(default=None, max_length=200)
    warehouse_name: str = Field(max_length=100)
    category: InventoryCategory
    product_id: uuid.UUID | None = None
    crude_product_id: uuid.UUID | None = None
    material_id: uuid.UUID | None = None
    quantity: Decimal = Field(default=Decimal("0"), decimal_places=4)
    unit: str = Field(default="個", max_length=20)
    standard_unit_price: Decimal = Field(default=Decimal("0"), decimal_places=4)
    valuation_amount: Decimal = Field(default=Decimal("0"), decimal_places=4)
    source_system: SourceSystem = SourceSystem.manual
    notes: str | None = None


class InventoryValuationCreate(InventoryValuationBase):
    pass


class InventoryValuationUpdate(BaseModel):
    item_name: str | None = None
    warehouse_name: str | None = None
    category: InventoryCategory | None = None
    quantity: Decimal | None = None
    unit: str | None = None
    standard_unit_price: Decimal | None = None
    valuation_amount: Decimal | None = None
    source_system: SourceSystem | None = None
    notes: str | None = None


class InventoryValuationRead(InventoryValuationBase):
    model_config = ConfigDict(from_attributes=True)
    id: uuid.UUID
    created_at: datetime
    updated_at: datetime


# --- Summary schemas ---

class CategorySummary(BaseModel):
    """区分別集計"""
    category: InventoryCategory
    item_count: int
    total_quantity: Decimal
    total_amount: Decimal


class WarehouseSummary(BaseModel):
    """倉庫別集計"""
    warehouse_name: str
    item_count: int
    total_amount: Decimal


class ValuationSummary(BaseModel):
    """在庫評価サマリ — 期間ごとの区分別・倉庫別集計"""
    period_id: uuid.UUID
    total_items: int
    total_amount: Decimal
    by_category: list[CategorySummary]
    by_warehouse: list[WarehouseSummary]


class ProductInventoryFlow(BaseModel):
    """製品ごとの期首+受入-払出=期末の在庫推移サマリ（標準単価ベース）"""
    product_id: uuid.UUID
    product_code: str
    product_name: str
    standard_unit_price: Decimal
    # 数量
    beginning_qty: Decimal = Decimal("0")     # 期首数量(前期末在庫評価から)
    receipt_qty: Decimal = Decimal("0")        # 受入数量(InventoryMovement: finished_goods等)
    issue_qty: Decimal = Decimal("0")          # 払出数量(InventoryMovement: research/promotion/adjustment等)
    ending_qty: Decimal = Decimal("0")         # 期末数量(当期末在庫評価から)
    # 金額(数量 × 標準単価)
    beginning_amount: Decimal = Decimal("0")
    receipt_amount: Decimal = Decimal("0")
    issue_amount: Decimal = Decimal("0")
    ending_amount: Decimal = Decimal("0")
