"""Pydantic v2 schemas for import batch tracking."""

import uuid
from datetime import datetime

from pydantic import BaseModel, ConfigDict

from app.models.audit import ImportStatus


class ImportErrorRead(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    id: uuid.UUID
    row_number: int
    column_name: str | None = None
    error_message: str
    raw_data: dict | None = None


class ImportBatchRead(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    id: uuid.UUID
    file_name: str
    source_system: str
    status: ImportStatus
    total_rows: int
    success_rows: int
    error_rows: int
    period_id: uuid.UUID | None = None
    started_at: datetime | None = None
    completed_at: datetime | None = None
    notes: str | None = None
    errors: list[ImportErrorRead] = []
    created_at: datetime
    updated_at: datetime


class ImportUploadResponse(BaseModel):
    batch_id: uuid.UUID
    status: ImportStatus
    total_rows: int
    success_rows: int
    error_rows: int
    errors: list[ImportErrorRead] = []
    message: str
