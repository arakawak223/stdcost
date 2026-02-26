"""Cost data ORM models: standard costs, actual costs, inventory movements, allocations.

設計方針:
- 標準原価計算が中核機能（BOMベースの積上計算、標準単価設定）
- 実際原価は簡素化した集計データとして取り込む（現行Excelの複雑な仕訳フローは再現しない）
- 差異分析 = 標準原価 vs 実際原価（簡素化版）
"""

import enum
import uuid
from datetime import date, datetime
from decimal import Decimal

from sqlalchemy import (
    Date,
    DateTime,
    Enum,
    ForeignKey,
    Integer,
    Numeric,
    String,
    Text,
    UniqueConstraint,
    func,
)
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.models.base import Base, TimestampMixin, UUIDPrimaryKeyMixin
from app.models.master import CostCenter, FiscalPeriod, Product, CrudeProduct


class SourceSystem(str, enum.Enum):
    """データソースシステム"""
    geneki_db = "geneki_db"        # 原液DB（Access）
    sc_system = "sc_system"        # SC（スーパーカクテル/基幹システム）
    kanjyo_bugyo = "kanjyo_bugyo"  # 勘定奉行
    tsuhan21 = "tsuhan21"          # 通販21
    romu_db = "romu_db"            # 労務DB
    product_db = "product_db"      # 製品管理DB
    manual = "manual"              # 手動入力


class MovementType(str, enum.Enum):
    """在庫移動区分（①-⑨の簡素化版）"""
    material_receipt = "material_receipt"    # ①原料入荷
    material_usage = "material_usage"       # ②原料使用（製造部へ）
    crude_increase = "crude_increase"       # ③原体増加（発酵完了）
    crude_output = "crude_output"           # ④原液出庫（ブレンド元）
    crude_input = "crude_input"             # ⑤原液入庫（ブレンド先）
    finished_goods = "finished_goods"       # ⑥完成品（製品課→倉庫）
    research = "research"                   # ⑦試験研究
    promotion = "promotion"                 # ⑧販促費
    adjustment = "adjustment"               # ⑨在庫調整


class CostElement(str, enum.Enum):
    """原価要素"""
    material = "material"          # 原材料費（原料費）
    crude_product = "crude_product"  # 原体原価
    packaging = "packaging"        # 資材費
    labor = "labor"                # 労務費
    overhead = "overhead"          # 経費（製造間接費）
    outsourcing = "outsourcing"    # 外注加工費
    prior_process = "prior_process"  # 前工程費


# --- 標準原価（中核モデル） ---

class StandardCost(UUIDPrimaryKeyMixin, TimestampMixin, Base):
    """標準原価 - BOMベースで積み上げた製品ごとの標準原価"""
    __tablename__ = "standard_costs"
    __table_args__ = (
        UniqueConstraint("product_id", "period_id", name="uq_std_cost_product_period"),
    )

    product_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), ForeignKey("products.id"), nullable=False, index=True
    )
    period_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), ForeignKey("fiscal_periods.id"), nullable=False, index=True
    )
    # 原価要素別内訳
    crude_product_cost: Mapped[Decimal] = mapped_column(Numeric(18, 4), nullable=False, default=0, comment="原体原価")
    packaging_cost: Mapped[Decimal] = mapped_column(Numeric(18, 4), nullable=False, default=0, comment="資材費")
    labor_cost: Mapped[Decimal] = mapped_column(Numeric(18, 4), nullable=False, default=0, comment="労務費")
    overhead_cost: Mapped[Decimal] = mapped_column(Numeric(18, 4), nullable=False, default=0, comment="経費")
    outsourcing_cost: Mapped[Decimal] = mapped_column(Numeric(18, 4), nullable=False, default=0, comment="外注加工費")
    total_cost: Mapped[Decimal] = mapped_column(Numeric(18, 4), nullable=False, default=0, comment="標準原価合計")
    unit_cost: Mapped[Decimal] = mapped_column(Numeric(18, 4), nullable=False, default=0, comment="製品単位あたり標準原価")
    lot_size: Mapped[Decimal] = mapped_column(Numeric(18, 4), nullable=False, default=1)
    notes: Mapped[str | None] = mapped_column(Text)

    product: Mapped[Product] = relationship("Product", lazy="selectin")
    period: Mapped[FiscalPeriod] = relationship("FiscalPeriod", lazy="selectin")


class CrudeProductStandardCost(UUIDPrimaryKeyMixin, TimestampMixin, Base):
    """原体標準原価 - 原体ごとの標準原価（製造部での計算結果）"""
    __tablename__ = "crude_product_standard_costs"
    __table_args__ = (
        UniqueConstraint("crude_product_id", "period_id", name="uq_crude_std_cost_product_period"),
    )

    crude_product_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), ForeignKey("crude_products.id"), nullable=False, index=True
    )
    period_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), ForeignKey("fiscal_periods.id"), nullable=False, index=True
    )
    material_cost: Mapped[Decimal] = mapped_column(Numeric(18, 4), nullable=False, default=0, comment="原材料費")
    labor_cost: Mapped[Decimal] = mapped_column(Numeric(18, 4), nullable=False, default=0, comment="労務費")
    overhead_cost: Mapped[Decimal] = mapped_column(Numeric(18, 4), nullable=False, default=0, comment="経費")
    prior_process_cost: Mapped[Decimal] = mapped_column(Numeric(18, 4), nullable=False, default=0, comment="前工程費")
    total_cost: Mapped[Decimal] = mapped_column(Numeric(18, 4), nullable=False, default=0, comment="標準原価合計")
    unit_cost: Mapped[Decimal] = mapped_column(Numeric(18, 4), nullable=False, default=0, comment="kg単価")
    standard_quantity: Mapped[Decimal] = mapped_column(Numeric(18, 4), nullable=False, default=0, comment="標準数量(kg)")
    notes: Mapped[str | None] = mapped_column(Text)

    crude_product: Mapped[CrudeProduct] = relationship("CrudeProduct", lazy="selectin")
    period: Mapped[FiscalPeriod] = relationship("FiscalPeriod", lazy="selectin")


# --- 実際原価（簡素化版） ---

class ActualCost(UUIDPrimaryKeyMixin, TimestampMixin, Base):
    """実際原価（簡素化版）- 各ソースシステムから集計済みデータを取り込む"""
    __tablename__ = "actual_costs"
    __table_args__ = (
        UniqueConstraint("product_id", "cost_center_id", "period_id", name="uq_act_cost_product_cc_period"),
    )

    product_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), ForeignKey("products.id"), nullable=False, index=True
    )
    cost_center_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), ForeignKey("cost_centers.id"), nullable=False, index=True
    )
    period_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), ForeignKey("fiscal_periods.id"), nullable=False, index=True
    )
    # 簡素化: 実際原価計算Excelの最終集計結果を格納
    crude_product_cost: Mapped[Decimal] = mapped_column(Numeric(18, 4), nullable=False, default=0, comment="原体原価")
    packaging_cost: Mapped[Decimal] = mapped_column(Numeric(18, 4), nullable=False, default=0, comment="資材費")
    labor_cost: Mapped[Decimal] = mapped_column(Numeric(18, 4), nullable=False, default=0, comment="労務費")
    overhead_cost: Mapped[Decimal] = mapped_column(Numeric(18, 4), nullable=False, default=0, comment="経費")
    outsourcing_cost: Mapped[Decimal] = mapped_column(Numeric(18, 4), nullable=False, default=0, comment="外注加工費")
    total_cost: Mapped[Decimal] = mapped_column(Numeric(18, 4), nullable=False, default=0)
    quantity_produced: Mapped[Decimal] = mapped_column(Numeric(18, 4), nullable=False, default=0)
    source_system: Mapped[SourceSystem] = mapped_column(
        Enum(SourceSystem), nullable=False, default=SourceSystem.manual
    )
    notes: Mapped[str | None] = mapped_column(Text)

    product: Mapped[Product] = relationship("Product", lazy="selectin")
    cost_center: Mapped[CostCenter] = relationship("CostCenter", lazy="selectin")
    period: Mapped[FiscalPeriod] = relationship("FiscalPeriod", lazy="selectin")


class CrudeProductActualCost(UUIDPrimaryKeyMixin, TimestampMixin, Base):
    """原体実際原価（簡素化版）- 製造部での原体別実際原価集計結果"""
    __tablename__ = "crude_product_actual_costs"
    __table_args__ = (
        UniqueConstraint("crude_product_id", "period_id", name="uq_crude_act_cost_product_period"),
    )

    crude_product_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), ForeignKey("crude_products.id"), nullable=False, index=True
    )
    period_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), ForeignKey("fiscal_periods.id"), nullable=False, index=True
    )
    material_cost: Mapped[Decimal] = mapped_column(Numeric(18, 4), nullable=False, default=0, comment="原材料費")
    labor_cost: Mapped[Decimal] = mapped_column(Numeric(18, 4), nullable=False, default=0, comment="労務費")
    overhead_cost: Mapped[Decimal] = mapped_column(Numeric(18, 4), nullable=False, default=0, comment="経費")
    prior_process_cost: Mapped[Decimal] = mapped_column(Numeric(18, 4), nullable=False, default=0, comment="前工程費")
    total_cost: Mapped[Decimal] = mapped_column(Numeric(18, 4), nullable=False, default=0)
    actual_quantity: Mapped[Decimal] = mapped_column(Numeric(18, 4), nullable=False, default=0, comment="実際数量(kg)")
    source_system: Mapped[SourceSystem] = mapped_column(
        Enum(SourceSystem), nullable=False, default=SourceSystem.geneki_db
    )
    notes: Mapped[str | None] = mapped_column(Text)

    crude_product: Mapped[CrudeProduct] = relationship("CrudeProduct", lazy="selectin")
    period: Mapped[FiscalPeriod] = relationship("FiscalPeriod", lazy="selectin")


# --- 在庫移動 ---

class InventoryMovement(UUIDPrimaryKeyMixin, TimestampMixin, Base):
    """在庫移動 - 原料/原体/製品の入出庫を追跡"""
    __tablename__ = "inventory_movements"

    product_id: Mapped[uuid.UUID | None] = mapped_column(
        UUID(as_uuid=True), ForeignKey("products.id"), index=True
    )
    crude_product_id: Mapped[uuid.UUID | None] = mapped_column(
        UUID(as_uuid=True), ForeignKey("crude_products.id"), index=True
    )
    material_id: Mapped[uuid.UUID | None] = mapped_column(
        UUID(as_uuid=True), ForeignKey("materials.id"), index=True
    )
    cost_center_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), ForeignKey("cost_centers.id"), nullable=False, index=True
    )
    period_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), ForeignKey("fiscal_periods.id"), nullable=False, index=True
    )
    movement_type: Mapped[MovementType] = mapped_column(Enum(MovementType), nullable=False)
    movement_date: Mapped[date] = mapped_column(Date, nullable=False)
    quantity: Mapped[Decimal] = mapped_column(Numeric(18, 4), nullable=False)
    unit_cost: Mapped[Decimal] = mapped_column(Numeric(18, 4), nullable=False, default=0)
    total_cost: Mapped[Decimal] = mapped_column(Numeric(18, 4), nullable=False, default=0)
    lot_number: Mapped[str | None] = mapped_column(String(50))
    aging_start_date: Mapped[date | None] = mapped_column(Date, comment="熟成開始日（原体用）")
    source_system: Mapped[SourceSystem] = mapped_column(
        Enum(SourceSystem), nullable=False, default=SourceSystem.manual
    )
    notes: Mapped[str | None] = mapped_column(Text)

    product: Mapped[Product | None] = relationship("Product", lazy="selectin")
    crude_product: Mapped[CrudeProduct | None] = relationship("CrudeProduct", lazy="selectin")
    material: Mapped["Material | None"] = relationship("Material", lazy="selectin")
    cost_center: Mapped[CostCenter] = relationship("CostCenter", lazy="selectin")
    period: Mapped[FiscalPeriod] = relationship("FiscalPeriod", lazy="selectin")


# --- 配賦 ---

class CostAllocation(UUIDPrimaryKeyMixin, TimestampMixin, Base):
    __tablename__ = "cost_allocations"

    rule_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), ForeignKey("allocation_rules.id"), nullable=False, index=True
    )
    period_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), ForeignKey("fiscal_periods.id"), nullable=False, index=True
    )
    source_cost_center_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), ForeignKey("cost_centers.id"), nullable=False
    )
    target_cost_center_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), ForeignKey("cost_centers.id"), nullable=False
    )
    cost_element: Mapped[CostElement | None] = mapped_column(Enum(CostElement), comment="配賦対象の原価要素")
    allocated_amount: Mapped[Decimal] = mapped_column(Numeric(18, 4), nullable=False)
    basis_quantity: Mapped[Decimal] = mapped_column(Numeric(18, 4), nullable=False)
    ratio: Mapped[Decimal] = mapped_column(Numeric(8, 4), nullable=False)
    executed_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now(), nullable=False
    )
    notes: Mapped[str | None] = mapped_column(Text)

    period: Mapped[FiscalPeriod] = relationship("FiscalPeriod", lazy="selectin")
