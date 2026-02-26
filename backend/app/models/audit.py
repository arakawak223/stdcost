"""Audit, import, reconciliation, and AI explanation ORM models."""

import enum
import uuid
from datetime import datetime

from sqlalchemy import DateTime, Enum, ForeignKey, Integer, Numeric, String, Text, func
from sqlalchemy.dialects.postgresql import JSON, UUID
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.models.base import Base, TimestampMixin, UUIDPrimaryKeyMixin
from app.models.master import FiscalPeriod


class AuditAction(str, enum.Enum):
    create = "create"
    update = "update"
    delete = "delete"


class ImportStatus(str, enum.Enum):
    pending = "pending"
    processing = "processing"
    completed = "completed"
    failed = "failed"


class ReconciliationStatus(str, enum.Enum):
    matched = "matched"
    unmatched = "unmatched"
    discrepancy = "discrepancy"


class ReviewStatus(str, enum.Enum):
    pending = "pending"
    approved = "approved"
    rejected = "rejected"


class AuditLog(UUIDPrimaryKeyMixin, Base):
    __tablename__ = "audit_logs"

    entity_type: Mapped[str] = mapped_column(String(50), nullable=False, index=True)
    entity_id: Mapped[str] = mapped_column(String(36), nullable=False, index=True)
    action: Mapped[AuditAction] = mapped_column(Enum(AuditAction), nullable=False)
    changes: Mapped[dict | None] = mapped_column(JSON)
    user_info: Mapped[str | None] = mapped_column(String(100))
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now(), nullable=False
    )


class ImportBatch(UUIDPrimaryKeyMixin, TimestampMixin, Base):
    __tablename__ = "import_batches"

    file_name: Mapped[str] = mapped_column(String(255), nullable=False)
    source_system: Mapped[str] = mapped_column(String(50), nullable=False)
    status: Mapped[ImportStatus] = mapped_column(
        Enum(ImportStatus), nullable=False, default=ImportStatus.pending
    )
    total_rows: Mapped[int] = mapped_column(Integer, default=0)
    success_rows: Mapped[int] = mapped_column(Integer, default=0)
    error_rows: Mapped[int] = mapped_column(Integer, default=0)
    period_id: Mapped[uuid.UUID | None] = mapped_column(
        UUID(as_uuid=True), ForeignKey("fiscal_periods.id")
    )
    started_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True))
    completed_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True))
    notes: Mapped[str | None] = mapped_column(Text)

    period: Mapped[FiscalPeriod | None] = relationship("FiscalPeriod", lazy="selectin")
    errors: Mapped[list["ImportError"]] = relationship("ImportError", back_populates="batch", lazy="selectin")


class ImportError(UUIDPrimaryKeyMixin, Base):
    __tablename__ = "import_errors"

    batch_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), ForeignKey("import_batches.id", ondelete="CASCADE"), nullable=False, index=True
    )
    row_number: Mapped[int] = mapped_column(Integer, nullable=False)
    column_name: Mapped[str | None] = mapped_column(String(100))
    error_message: Mapped[str] = mapped_column(Text, nullable=False)
    raw_data: Mapped[dict | None] = mapped_column(JSON)

    batch: Mapped[ImportBatch] = relationship("ImportBatch", back_populates="errors")


class ReconciliationResult(UUIDPrimaryKeyMixin, TimestampMixin, Base):
    __tablename__ = "reconciliation_results"

    period_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), ForeignKey("fiscal_periods.id"), nullable=False, index=True
    )
    entity_type: Mapped[str] = mapped_column(String(50), nullable=False)
    entity_id: Mapped[str] = mapped_column(String(36), nullable=False)
    source_a: Mapped[str] = mapped_column(String(50), nullable=False)
    source_b: Mapped[str] = mapped_column(String(50), nullable=False)
    value_a: Mapped[str | None] = mapped_column(Numeric(18, 4))
    value_b: Mapped[str | None] = mapped_column(Numeric(18, 4))
    difference: Mapped[str | None] = mapped_column(Numeric(18, 4))
    status: Mapped[ReconciliationStatus] = mapped_column(Enum(ReconciliationStatus), nullable=False)
    notes: Mapped[str | None] = mapped_column(Text)

    period: Mapped[FiscalPeriod] = relationship("FiscalPeriod", lazy="selectin")


class AIExplanation(UUIDPrimaryKeyMixin, TimestampMixin, Base):
    __tablename__ = "ai_explanations"

    context_type: Mapped[str] = mapped_column(String(50), nullable=False, index=True)
    context_id: Mapped[str | None] = mapped_column(String(36))
    prompt: Mapped[str] = mapped_column(Text, nullable=False)
    response: Mapped[str] = mapped_column(Text, nullable=False)
    model: Mapped[str] = mapped_column(String(50), nullable=False)
    input_tokens: Mapped[int] = mapped_column(Integer, default=0)
    output_tokens: Mapped[int] = mapped_column(Integer, default=0)
    review_status: Mapped[ReviewStatus] = mapped_column(
        Enum(ReviewStatus), nullable=False, default=ReviewStatus.pending
    )
    reviewer_notes: Mapped[str | None] = mapped_column(Text)
