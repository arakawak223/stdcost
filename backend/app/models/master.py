"""Master data ORM models: cost centers, materials, products, crude products, BOM, allocation rules, fiscal periods, outsourcing."""

import enum
import uuid
from datetime import date
from decimal import Decimal

from sqlalchemy import (
    Boolean,
    Date,
    Enum,
    ForeignKey,
    Integer,
    Numeric,
    String,
    Text,
    UniqueConstraint,
)
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.models.base import Base, TimestampMixin, UUIDPrimaryKeyMixin


# --- Enums ---

class CostCenterType(str, enum.Enum):
    """部門区分: 製造部 / 製品課 / 間接部門"""
    manufacturing = "manufacturing"  # 製造部（原体原価計算の主体）
    product = "product"              # 製品課（製品原価計算の主体）
    indirect = "indirect"            # 間接部門


class MaterialCategory(str, enum.Enum):
    """原材料カテゴリ（実際の万田発酵の原料分類）"""
    fruit = "fruit"            # 果物（リンゴ、カキ、バナナ等）
    vegetable = "vegetable"    # 野菜（ニンジン、ゴボウ等）
    grain = "grain"            # 穀物（玄米、大麦等）
    seaweed = "seaweed"        # 海藻（ヒジキ、ワカメ等）
    other = "other"            # その他（黒砂糖、ゴマ等）


class MaterialType(str, enum.Enum):
    """原材料種別"""
    raw = "raw"                # 原料（果物・野菜・穀物等）
    packaging = "packaging"    # 資材（容器・ラベル・段ボール等）
    sub_material = "sub_material"  # 副資材


class CrudeProductType(str, enum.Enum):
    """原体種別（発酵タイプ）"""
    R = "R"        # レギュラー
    HI = "HI"      # HI（ハイグレード）
    G = "G"        # ゴールド
    SP = "SP"      # スペシャル
    GN = "GN"      # ジンジャー
    other = "other"


class ProductType(str, enum.Enum):
    """製品区分（製品課での分類）"""
    semi_finished = "semi_finished"            # 半製品
    in_house_product_dept = "in_house_product_dept"  # 内製品（製品課）
    in_house_manufacturing = "in_house_manufacturing"  # 内製品（製造部）
    outsourced_in_house = "outsourced_in_house"  # 外注内製
    outsourced = "outsourced"                    # 外注品
    special = "special"                          # 特殊
    produce = "produce"                          # 産品


class BomType(str, enum.Enum):
    raw_material_process = "raw_material_process"  # 原体工程（原料→原体）
    product_process = "product_process"            # 製品工程（原体→製品）


class PeriodStatus(str, enum.Enum):
    open = "open"
    closing = "closing"
    closed = "closed"


class AllocationBasis(str, enum.Enum):
    """配賦基準"""
    production_hours = "production_hours"         # 直接生産時間（労務費配賦）
    raw_material_quantity = "raw_material_quantity"  # 原料使用数量（経費配賦）
    crude_quantity = "crude_quantity"              # 原体数量
    weight_based = "weight_based"                 # 重量基準
    manual = "manual"                             # 手動設定


# --- Models ---

class CostCenter(UUIDPrimaryKeyMixin, TimestampMixin, Base):
    """部門マスタ - 製造部（原体原価計算）と製品課（製品原価計算）の2部門が中核"""
    __tablename__ = "cost_centers"

    code: Mapped[str] = mapped_column(String(20), unique=True, nullable=False, index=True)
    name: Mapped[str] = mapped_column(String(100), nullable=False)
    name_short: Mapped[str | None] = mapped_column(String(50))
    center_type: Mapped[CostCenterType] = mapped_column(Enum(CostCenterType), nullable=False)
    parent_id: Mapped[uuid.UUID | None] = mapped_column(
        UUID(as_uuid=True), ForeignKey("cost_centers.id"), index=True
    )
    is_active: Mapped[bool] = mapped_column(Boolean, default=True, nullable=False)
    sort_order: Mapped[int] = mapped_column(Integer, default=0)

    parent: Mapped["CostCenter | None"] = relationship("CostCenter", remote_side="CostCenter.id", lazy="selectin")
    children: Mapped[list["CostCenter"]] = relationship("CostCenter", back_populates="parent", lazy="selectin")


class Material(UUIDPrimaryKeyMixin, TimestampMixin, Base):
    """原材料マスタ - 果物・野菜・穀物・海藻等の実原料と資材"""
    __tablename__ = "materials"

    code: Mapped[str] = mapped_column(String(20), unique=True, nullable=False, index=True)
    name: Mapped[str] = mapped_column(String(200), nullable=False)
    material_type: Mapped[MaterialType] = mapped_column(Enum(MaterialType), nullable=False)
    category: Mapped[MaterialCategory | None] = mapped_column(Enum(MaterialCategory))
    unit: Mapped[str] = mapped_column(String(10), nullable=False)
    standard_unit_price: Mapped[Decimal] = mapped_column(Numeric(18, 4), nullable=False, default=0)
    is_active: Mapped[bool] = mapped_column(Boolean, default=True, nullable=False)
    notes: Mapped[str | None] = mapped_column(Text)


class CrudeProduct(UUIDPrimaryKeyMixin, TimestampMixin, Base):
    """原体（原液）マスタ - 万田発酵の中核。年度+タイプで管理（例: 38R, 38HI, 38G）
    発酵食品は3年以上熟成される。前工程で複数原体をブレンドすることもある。"""
    __tablename__ = "crude_products"
    __table_args__ = (
        UniqueConstraint("code", name="uq_crude_product_code"),
    )

    code: Mapped[str] = mapped_column(String(20), unique=True, nullable=False, index=True)
    name: Mapped[str] = mapped_column(String(200), nullable=False)
    vintage_year: Mapped[int | None] = mapped_column(Integer, comment="仕込み年度（和暦の年数、例: 38=第38期）")
    crude_type: Mapped[CrudeProductType] = mapped_column(Enum(CrudeProductType), nullable=False)
    aging_years: Mapped[int | None] = mapped_column(Integer, comment="熟成年数")
    is_blend: Mapped[bool] = mapped_column(Boolean, default=False, comment="ブレンド品（前工程あり）かどうか")
    blend_source_ids: Mapped[str | None] = mapped_column(Text, comment="ブレンド元の原体コード（JSON配列）")
    unit: Mapped[str] = mapped_column(String(10), nullable=False, default="kg")
    is_active: Mapped[bool] = mapped_column(Boolean, default=True, nullable=False)
    notes: Mapped[str | None] = mapped_column(Text)


class Product(UUIDPrimaryKeyMixin, TimestampMixin, Base):
    """製品マスタ - SC（スーパーカクテル）のコードで管理、製品課で原価計算"""
    __tablename__ = "products"

    code: Mapped[str] = mapped_column(String(20), unique=True, nullable=False, index=True)
    name: Mapped[str] = mapped_column(String(200), nullable=False)
    name_short: Mapped[str | None] = mapped_column(String(50))
    product_group: Mapped[str | None] = mapped_column(String(50), index=True)
    product_type: Mapped[ProductType] = mapped_column(
        Enum(ProductType), nullable=False, default=ProductType.in_house_product_dept
    )
    sc_code: Mapped[str | None] = mapped_column(String(30), index=True, comment="SCシステムの品目コード")
    content_weight_g: Mapped[Decimal | None] = mapped_column(Numeric(10, 2), comment="内容量(g)")
    product_symbol: Mapped[str | None] = mapped_column(String(20), comment="製品記号")
    gram_unit_price: Mapped[Decimal | None] = mapped_column(Numeric(18, 6), comment="グラム単価")
    unit: Mapped[str] = mapped_column(String(10), nullable=False, default="個")
    standard_lot_size: Mapped[Decimal] = mapped_column(Numeric(18, 4), nullable=False, default=1)
    is_active: Mapped[bool] = mapped_column(Boolean, default=True, nullable=False)
    notes: Mapped[str | None] = mapped_column(Text)

    bom_headers: Mapped[list["BomHeader"]] = relationship("BomHeader", back_populates="product", lazy="selectin")


class Contractor(UUIDPrimaryKeyMixin, TimestampMixin, Base):
    """外注先マスタ - 外注加工を行う業者"""
    __tablename__ = "contractors"

    code: Mapped[str] = mapped_column(String(20), unique=True, nullable=False, index=True)
    name: Mapped[str] = mapped_column(String(200), nullable=False)
    name_short: Mapped[str | None] = mapped_column(String(50))
    is_active: Mapped[bool] = mapped_column(Boolean, default=True, nullable=False)
    notes: Mapped[str | None] = mapped_column(Text)


class BomHeader(UUIDPrimaryKeyMixin, TimestampMixin, Base):
    __tablename__ = "bom_headers"
    __table_args__ = (
        UniqueConstraint("product_id", "bom_type", "effective_date", name="uq_bom_product_type_date"),
        UniqueConstraint("crude_product_id", "bom_type", "effective_date", name="uq_bom_crude_type_date"),
    )

    product_id: Mapped[uuid.UUID | None] = mapped_column(
        UUID(as_uuid=True), ForeignKey("products.id"), nullable=True, index=True
    )
    crude_product_id: Mapped[uuid.UUID | None] = mapped_column(
        UUID(as_uuid=True), ForeignKey("crude_products.id"), nullable=True, index=True,
        comment="Stage 1 BOM: 原体を出力する場合"
    )
    bom_type: Mapped[BomType] = mapped_column(Enum(BomType), nullable=False)
    effective_date: Mapped[date] = mapped_column(Date, nullable=False)
    version: Mapped[int] = mapped_column(Integer, default=1)
    yield_rate: Mapped[Decimal] = mapped_column(Numeric(8, 4), default=Decimal("1.0000"))
    is_active: Mapped[bool] = mapped_column(Boolean, default=True, nullable=False)
    notes: Mapped[str | None] = mapped_column(Text)

    product: Mapped[Product | None] = relationship("Product", back_populates="bom_headers", lazy="selectin")
    crude_product: Mapped["CrudeProduct | None"] = relationship("CrudeProduct", lazy="selectin")
    lines: Mapped[list["BomLine"]] = relationship("BomLine", back_populates="header", lazy="selectin", cascade="all, delete-orphan")


class BomLine(UUIDPrimaryKeyMixin, TimestampMixin, Base):
    __tablename__ = "bom_lines"

    header_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), ForeignKey("bom_headers.id", ondelete="CASCADE"), nullable=False, index=True
    )
    material_id: Mapped[uuid.UUID | None] = mapped_column(
        UUID(as_uuid=True), ForeignKey("materials.id")
    )
    crude_product_id: Mapped[uuid.UUID | None] = mapped_column(
        UUID(as_uuid=True), ForeignKey("crude_products.id"), comment="原体を使う場合"
    )
    quantity: Mapped[Decimal] = mapped_column(Numeric(18, 6), nullable=False)
    unit: Mapped[str] = mapped_column(String(10), nullable=False)
    loss_rate: Mapped[Decimal] = mapped_column(Numeric(8, 4), default=Decimal("0.0000"))
    sort_order: Mapped[int] = mapped_column(Integer, default=0)
    notes: Mapped[str | None] = mapped_column(Text)

    header: Mapped[BomHeader] = relationship("BomHeader", back_populates="lines")
    material: Mapped[Material | None] = relationship("Material", lazy="selectin")
    crude_product: Mapped[CrudeProduct | None] = relationship("CrudeProduct", lazy="selectin")


class AllocationRule(UUIDPrimaryKeyMixin, TimestampMixin, Base):
    __tablename__ = "allocation_rules"

    name: Mapped[str] = mapped_column(String(100), nullable=False)
    source_cost_center_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), ForeignKey("cost_centers.id"), nullable=False
    )
    basis: Mapped[AllocationBasis] = mapped_column(
        Enum(AllocationBasis), nullable=False, default=AllocationBasis.raw_material_quantity
    )
    is_active: Mapped[bool] = mapped_column(Boolean, default=True, nullable=False)
    notes: Mapped[str | None] = mapped_column(Text)

    source_cost_center: Mapped[CostCenter] = relationship("CostCenter", lazy="selectin")
    targets: Mapped[list["AllocationRuleTarget"]] = relationship(
        "AllocationRuleTarget", back_populates="rule", lazy="selectin"
    )


class AllocationRuleTarget(UUIDPrimaryKeyMixin, TimestampMixin, Base):
    __tablename__ = "allocation_rule_targets"

    rule_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), ForeignKey("allocation_rules.id", ondelete="CASCADE"), nullable=False, index=True
    )
    target_cost_center_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), ForeignKey("cost_centers.id"), nullable=False
    )
    ratio: Mapped[Decimal] = mapped_column(Numeric(8, 4), nullable=False)

    rule: Mapped[AllocationRule] = relationship("AllocationRule", back_populates="targets")
    target_cost_center: Mapped[CostCenter] = relationship("CostCenter", lazy="selectin")


class FiscalPeriod(UUIDPrimaryKeyMixin, TimestampMixin, Base):
    __tablename__ = "fiscal_periods"
    __table_args__ = (
        UniqueConstraint("year", "month", name="uq_fiscal_period_year_month"),
    )

    year: Mapped[int] = mapped_column(Integer, nullable=False, comment="期数（例: 38=第38期）")
    month: Mapped[int] = mapped_column(Integer, nullable=False)
    start_date: Mapped[date] = mapped_column(Date, nullable=False)
    end_date: Mapped[date] = mapped_column(Date, nullable=False)
    status: Mapped[PeriodStatus] = mapped_column(
        Enum(PeriodStatus), nullable=False, default=PeriodStatus.open
    )
    notes: Mapped[str | None] = mapped_column(Text)


class CostBudget(UUIDPrimaryKeyMixin, TimestampMixin, Base):
    """部門別予算マスタ - 部門×期間ごとの労務費・経費・外注費予算"""
    __tablename__ = "cost_budgets"
    __table_args__ = (
        UniqueConstraint("cost_center_id", "period_id", name="uq_cost_budget_cc_period"),
    )

    cost_center_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), ForeignKey("cost_centers.id"), nullable=False, index=True
    )
    period_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), ForeignKey("fiscal_periods.id"), nullable=False, index=True
    )
    labor_budget: Mapped[Decimal] = mapped_column(Numeric(18, 4), nullable=False, default=0, comment="労務費予算")
    overhead_budget: Mapped[Decimal] = mapped_column(Numeric(18, 4), nullable=False, default=0, comment="経費予算")
    outsourcing_budget: Mapped[Decimal] = mapped_column(Numeric(18, 4), nullable=False, default=0, comment="外注費予算")
    notes: Mapped[str | None] = mapped_column(Text)

    cost_center: Mapped[CostCenter] = relationship("CostCenter", lazy="selectin")
    period: Mapped[FiscalPeriod] = relationship("FiscalPeriod", lazy="selectin")
