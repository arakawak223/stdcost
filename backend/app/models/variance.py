"""Variance record ORM model."""

import enum
import uuid
from decimal import Decimal

from sqlalchemy import Boolean, Enum, ForeignKey, Numeric, String, Text
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.models.base import Base, TimestampMixin, UUIDPrimaryKeyMixin
from app.models.master import CostCenter, FiscalPeriod, Product


class VarianceType(str, enum.Enum):
    price = "price"
    quantity = "quantity"
    efficiency = "efficiency"
    mix = "mix"
    volume = "volume"


class VarianceRecord(UUIDPrimaryKeyMixin, TimestampMixin, Base):
    __tablename__ = "variance_records"

    product_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), ForeignKey("products.id"), nullable=False, index=True
    )
    cost_center_id: Mapped[uuid.UUID | None] = mapped_column(
        UUID(as_uuid=True), ForeignKey("cost_centers.id"), index=True
    )
    period_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), ForeignKey("fiscal_periods.id"), nullable=False, index=True
    )
    variance_type: Mapped[VarianceType] = mapped_column(Enum(VarianceType), nullable=False)
    cost_element: Mapped[str] = mapped_column(String(50), nullable=False)
    standard_amount: Mapped[Decimal] = mapped_column(Numeric(18, 4), nullable=False)
    actual_amount: Mapped[Decimal] = mapped_column(Numeric(18, 4), nullable=False)
    variance_amount: Mapped[Decimal] = mapped_column(Numeric(18, 4), nullable=False)
    variance_percent: Mapped[Decimal] = mapped_column(Numeric(8, 4), nullable=False, default=0)
    is_favorable: Mapped[bool] = mapped_column(nullable=False)
    is_flagged: Mapped[bool] = mapped_column(default=False, nullable=False)
    flag_reason: Mapped[str | None] = mapped_column(Text)
    notes: Mapped[str | None] = mapped_column(Text)

    product: Mapped[Product] = relationship("Product", lazy="selectin")
    cost_center: Mapped[CostCenter | None] = relationship("CostCenter", lazy="selectin")
    period: Mapped[FiscalPeriod] = relationship("FiscalPeriod", lazy="selectin")
