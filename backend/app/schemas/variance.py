"""Pydantic v2 schemas for variance analysis."""

import uuid
from datetime import datetime
from decimal import Decimal

from pydantic import BaseModel, ConfigDict, Field

from app.models.variance import VarianceType


# --- VarianceRecord CRUD ---

class VarianceRecordRead(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    id: uuid.UUID
    product_id: uuid.UUID
    cost_center_id: uuid.UUID | None = None
    period_id: uuid.UUID
    variance_type: VarianceType
    cost_element: str
    standard_amount: Decimal
    actual_amount: Decimal
    variance_amount: Decimal
    variance_percent: Decimal
    is_favorable: bool
    is_flagged: bool
    flag_reason: str | None = None
    notes: str | None = None
    created_at: datetime
    updated_at: datetime


class VarianceRecordUpdate(BaseModel):
    is_flagged: bool | None = None
    flag_reason: str | None = None
    notes: str | None = None


# --- Analysis Request/Response ---

class VarianceAnalysisRequest(BaseModel):
    period_id: uuid.UUID
    product_ids: list[uuid.UUID] | None = None
    threshold_percent: Decimal = Field(
        default=Decimal("5.0"),
        description="差異率がこの閾値を超えるレコードを自動フラグ",
    )


class CostElementVariance(BaseModel):
    cost_element: str
    standard_amount: Decimal
    actual_amount: Decimal
    variance_amount: Decimal
    variance_percent: Decimal
    is_favorable: bool


class ProductVarianceDetail(BaseModel):
    product_id: uuid.UUID
    product_code: str
    product_name: str
    cost_center_id: uuid.UUID | None = None
    cost_center_name: str | None = None
    total_standard: Decimal
    total_actual: Decimal
    total_variance: Decimal
    total_variance_percent: Decimal
    is_favorable: bool
    elements: list[CostElementVariance] = []


class VarianceAnalysisResult(BaseModel):
    period_id: uuid.UUID
    products_analyzed: int
    records_created: int
    flagged_count: int
    total_standard: Decimal
    total_actual: Decimal
    total_variance: Decimal
    details: list[ProductVarianceDetail] = []


# --- Summary Report ---

class VarianceSummaryItem(BaseModel):
    cost_element: str
    total_standard: Decimal
    total_actual: Decimal
    total_variance: Decimal
    average_variance_percent: Decimal
    favorable_count: int
    unfavorable_count: int
    flagged_count: int


class VarianceSummaryReport(BaseModel):
    period_id: uuid.UUID
    total_products: int
    total_records: int
    total_flagged: int
    overall_standard: Decimal
    overall_actual: Decimal
    overall_variance: Decimal
    by_element: list[VarianceSummaryItem] = []
