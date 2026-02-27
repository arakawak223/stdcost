"""Pydantic v2 schemas for reconciliation (Phase 6)."""

import uuid
from datetime import datetime
from decimal import Decimal

from pydantic import BaseModel, ConfigDict, Field

from app.models.audit import ReconciliationStatus


class ReconciliationResultRead(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    id: uuid.UUID
    period_id: uuid.UUID
    entity_type: str
    entity_id: str
    source_a: str
    source_b: str
    value_a: Decimal | None = None
    value_b: Decimal | None = None
    difference: Decimal | None = None
    status: ReconciliationStatus
    notes: str | None = None
    created_at: datetime
    updated_at: datetime


class ReconcileRequest(BaseModel):
    period_id: uuid.UUID
    threshold: Decimal = Field(
        default=Decimal("1000"),
        description="差額がこの閾値以下ならmatched",
    )


class ReconciliationSummary(BaseModel):
    period_id: uuid.UUID
    total: int
    matched: int
    unmatched: int
    discrepancy: int


class ReconcileResponse(BaseModel):
    summary: ReconciliationSummary
    results: list[ReconciliationResultRead]
    message: str
