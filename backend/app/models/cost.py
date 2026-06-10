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
from sqlalchemy.dialects.postgresql import JSONB, UUID
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.models.base import Base, TimestampMixin, UUIDPrimaryKeyMixin
from app.models.master import CostCenter, FiscalPeriod, Product, CrudeProduct, Material


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


class InventoryCategory(str, enum.Enum):
    """在庫区分（Excel「4.3期末全在庫」シートの「商品区分名」列）"""
    product = "product"                # 製品（自社製造）
    semi_finished = "semi_finished"    # 半製品
    crude_product = "crude_product"    # 原体（原液）
    raw_material = "raw_material"      # 原材料
    sub_material = "sub_material"      # 副資材
    merchandise = "merchandise"        # 商品（外注/仕入）
    other = "other"                    # その他


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


class WipStandardCost(UUIDPrimaryKeyMixin, TimestampMixin, Base):
    """仕掛品(半製品)標準単価(期別) - SC計算上の名寄せキー × 期間 で単価を管理。

    データソース: `docs/reference/決算用SC仕掛品.xlsx`
        - 「仕掛品標準単価一覧表（貼付）」シート (38件のキー別単価)
        - 「仕掛品名寄（貼付）」シート (469件の番手付きコード→種類マッピング)
    在庫評価では Product.sc_consolidation_key 経由で WIP の SC 単価を取得する。
    """
    __tablename__ = "wip_standard_costs"
    __table_args__ = (
        UniqueConstraint(
            "consolidation_key", "period_id",
            name="uq_wip_std_cost_key_period",
        ),
    )

    consolidation_key: Mapped[str] = mapped_column(
        String(50), nullable=False, index=True,
        comment="名寄せキー(B/BM/FB/G/GP/MP/O/P等)",
    )
    period_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), ForeignKey("fiscal_periods.id"), nullable=False, index=True
    )
    unit_cost: Mapped[Decimal] = mapped_column(
        Numeric(12, 4), nullable=False, comment="SC単価合計(¥/kg)"
    )
    pre_process_cost: Mapped[Decimal] = mapped_column(
        Numeric(12, 4), nullable=False, default=0, comment="前工程費(¥/kg)"
    )
    material_cost: Mapped[Decimal] = mapped_column(
        Numeric(12, 4), nullable=False, default=0, comment="原材料費(¥/kg)"
    )
    labor_cost: Mapped[Decimal] = mapped_column(
        Numeric(12, 4), nullable=False, default=0, comment="労務費(¥/kg)"
    )
    expense_cost: Mapped[Decimal] = mapped_column(
        Numeric(12, 4), nullable=False, default=0, comment="経費(¥/kg)"
    )
    effective_date: Mapped[date | None] = mapped_column(Date, comment="適用開始日(参考)")
    notes: Mapped[str | None] = mapped_column(Text)

    period: Mapped[FiscalPeriod] = relationship("FiscalPeriod", lazy="selectin")


class MaterialStandardCost(UUIDPrimaryKeyMixin, TimestampMixin, Base):
    """原材料標準単価(期別) - 原材料の標準単価を期ごとに管理。

    旧 Material.standard_unit_price (単一値) を発展させ、期別履歴・
    SC決算用の単価変更を扱えるようにしたもの。読出し時は当該期間の
    値を優先し、未設定なら Material.standard_unit_price (キャッシュ)
    にフォールバックする。
    """
    __tablename__ = "material_standard_costs"
    __table_args__ = (
        UniqueConstraint("material_id", "period_id", name="uq_material_std_cost_material_period"),
    )

    material_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), ForeignKey("materials.id", ondelete="CASCADE"), nullable=False, index=True
    )
    period_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), ForeignKey("fiscal_periods.id"), nullable=False, index=True
    )
    unit_cost: Mapped[Decimal] = mapped_column(Numeric(12, 4), nullable=False, comment="円/単位")
    effective_date: Mapped[date | None] = mapped_column(Date, comment="適用開始日(参考)")
    notes: Mapped[str | None] = mapped_column(Text)

    material: Mapped[Material] = relationship("Material", lazy="selectin")
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


# --- 前年実績 (F-01) ---

class PriorYearActual(UUIDPrimaryKeyMixin, TimestampMixin, Base):
    """前年(38期)製品実績SC原価 - 30SC製品rev1.xlsx 「5.製品」シート由来。

    年度全体集計(月別ではなく fiscal_year 単位)。差異分析の前期比較ベース。
    主要6項目は数量・単価・原価の3列セット、振替系7項目 (販促費DM/販促費/
    試験研究費/接待交際費/寄付金/広告宣伝費/在庫調整) は transfer_items
    JSONB に集約。
    """
    __tablename__ = "prior_year_actuals"
    __table_args__ = (
        UniqueConstraint("fiscal_year", "product_code", name="uq_prior_year_actual_year_code"),
    )

    fiscal_year: Mapped[int] = mapped_column(Integer, nullable=False, index=True, comment="会計年度(38=第38期)")
    category: Mapped[str | None] = mapped_column(String(20), comment="製造/仕入/製造振替/AB")
    product_code: Mapped[str] = mapped_column(String(50), nullable=False, index=True)
    product_name: Mapped[str | None] = mapped_column(String(200))
    product_id: Mapped[uuid.UUID | None] = mapped_column(
        UUID(as_uuid=True), ForeignKey("products.id"), index=True
    )

    # 期首商品棚卸高
    opening_qty: Mapped[Decimal] = mapped_column(Numeric(18, 4), nullable=False, default=0)
    opening_unit_price: Mapped[Decimal] = mapped_column(Numeric(18, 6), nullable=False, default=0)
    opening_cost: Mapped[Decimal] = mapped_column(Numeric(18, 2), nullable=False, default=0)

    # 当期商品製造･仕入原価
    manufacturing_qty: Mapped[Decimal] = mapped_column(Numeric(18, 4), nullable=False, default=0)
    manufacturing_unit_price: Mapped[Decimal] = mapped_column(Numeric(18, 6), nullable=False, default=0)
    manufacturing_cost: Mapped[Decimal] = mapped_column(Numeric(18, 2), nullable=False, default=0)

    # 振替
    transfer_qty: Mapped[Decimal] = mapped_column(Numeric(18, 4), nullable=False, default=0)
    transfer_unit_price: Mapped[Decimal] = mapped_column(Numeric(18, 6), nullable=False, default=0)
    transfer_cost: Mapped[Decimal] = mapped_column(Numeric(18, 2), nullable=False, default=0)

    # 当期商品売上原価
    cogs_qty: Mapped[Decimal] = mapped_column(Numeric(18, 4), nullable=False, default=0)
    cogs_unit_price: Mapped[Decimal] = mapped_column(Numeric(18, 6), nullable=False, default=0)
    cogs_cost: Mapped[Decimal] = mapped_column(Numeric(18, 2), nullable=False, default=0)

    # 外注支給分
    outsource_supply_qty: Mapped[Decimal] = mapped_column(Numeric(18, 4), nullable=False, default=0)
    outsource_supply_unit_price: Mapped[Decimal] = mapped_column(Numeric(18, 6), nullable=False, default=0)
    outsource_supply_cost: Mapped[Decimal] = mapped_column(Numeric(18, 2), nullable=False, default=0)

    # 期末商品棚卸高
    closing_qty: Mapped[Decimal] = mapped_column(Numeric(18, 4), nullable=False, default=0)
    closing_unit_price: Mapped[Decimal] = mapped_column(Numeric(18, 6), nullable=False, default=0)
    closing_cost: Mapped[Decimal] = mapped_column(Numeric(18, 2), nullable=False, default=0)

    # 振替系7項目 {key: {qty, cost}}
    transfer_items: Mapped[dict] = mapped_column(JSONB, nullable=False, default=dict)

    source_file: Mapped[str | None] = mapped_column(String(255))
    source_sheet: Mapped[str | None] = mapped_column(String(100))
    import_batch_id: Mapped[uuid.UUID | None] = mapped_column(
        UUID(as_uuid=True), ForeignKey("import_batches.id")
    )
    notes: Mapped[str | None] = mapped_column(Text)

    product: Mapped[Product | None] = relationship("Product", lazy="selectin")


class PriorYearMaterialActual(UUIDPrimaryKeyMixin, TimestampMixin, Base):
    """前年(38期)原材料実績SC原価 - 10 SC原材料.xlsx 「原材料SC明細」シート由来。

    年度全体集計(月別ではなく fiscal_year 単位)。差異分析の前期比較ベース。
    主要4項目 (期首棚卸/当期仕入高/当期投入高/期末棚卸) は数量・原価の2列セット。
    調整系7項目 (検査・分析/試用/返品/ロス分/廃棄処分/在庫調整/その他調整) は
    adjustment_items JSONB に集約。SC単価は原料単位の単一カラム。
    """
    __tablename__ = "prior_year_material_actuals"
    __table_args__ = (
        UniqueConstraint(
            "fiscal_year", "material_code", name="uq_prior_year_material_actual_year_code"
        ),
    )

    fiscal_year: Mapped[int] = mapped_column(Integer, nullable=False, index=True, comment="会計年度(38=第38期)")
    material_code: Mapped[str] = mapped_column(String(50), nullable=False, index=True)
    material_name: Mapped[str | None] = mapped_column(String(200))
    material_id: Mapped[uuid.UUID | None] = mapped_column(
        UUID(as_uuid=True), ForeignKey("materials.id"), index=True
    )
    sc_unit_price: Mapped[Decimal] = mapped_column(Numeric(18, 6), nullable=False, default=0)
    unit: Mapped[str | None] = mapped_column(String(20))

    # 期首棚卸
    opening_qty: Mapped[Decimal] = mapped_column(Numeric(18, 4), nullable=False, default=0)
    opening_cost: Mapped[Decimal] = mapped_column(Numeric(18, 2), nullable=False, default=0)
    # 当期仕入高
    purchase_qty: Mapped[Decimal] = mapped_column(Numeric(18, 4), nullable=False, default=0)
    purchase_cost: Mapped[Decimal] = mapped_column(Numeric(18, 2), nullable=False, default=0)
    # 当期投入高
    input_qty: Mapped[Decimal] = mapped_column(Numeric(18, 4), nullable=False, default=0)
    input_cost: Mapped[Decimal] = mapped_column(Numeric(18, 2), nullable=False, default=0)
    # 期末棚卸
    closing_qty: Mapped[Decimal] = mapped_column(Numeric(18, 4), nullable=False, default=0)
    closing_cost: Mapped[Decimal] = mapped_column(Numeric(18, 2), nullable=False, default=0)

    # 調整系7項目 {key: {label, qty, cost}}
    adjustment_items: Mapped[dict] = mapped_column(JSONB, nullable=False, default=dict)

    source_file: Mapped[str | None] = mapped_column(String(255))
    source_sheet: Mapped[str | None] = mapped_column(String(100))
    import_batch_id: Mapped[uuid.UUID | None] = mapped_column(
        UUID(as_uuid=True), ForeignKey("import_batches.id")
    )
    notes: Mapped[str | None] = mapped_column(Text)

    material: Mapped[Material | None] = relationship("Material", lazy="selectin")


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


# --- 在庫評価 ---

class InventoryValuation(UUIDPrimaryKeyMixin, TimestampMixin, Base):
    """期末在庫評価 - 標準単価×実際数量で在庫金額を算出

    Excel「4.3期末全在庫」シートの 商品コード×倉庫名×期間 単位の在庫数量を保持し、
    StandardCost / CrudeProductStandardCost / Material.standard_unit_price から
    標準単価を引いて評価金額を算出する。
    """
    __tablename__ = "inventory_valuations"
    __table_args__ = (
        UniqueConstraint(
            "item_code", "warehouse_name", "period_id",
            name="uq_inv_val_code_wh_period"
        ),
    )

    period_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), ForeignKey("fiscal_periods.id"), nullable=False, index=True
    )
    item_code: Mapped[str] = mapped_column(
        String(30), nullable=False, index=True,
        comment="商品コード（マスタ未登録分: 例 (有償)20220500015 等にも対応）"
    )
    item_name: Mapped[str | None] = mapped_column(String(200), comment="商品名（参考情報）")
    warehouse_name: Mapped[str] = mapped_column(String(100), nullable=False, index=True, comment="倉庫名")
    category: Mapped[InventoryCategory] = mapped_column(Enum(InventoryCategory), nullable=False, index=True)
    # マスタ参照（item_code から解決して埋める。マスタ未登録の場合はNULL）
    product_id: Mapped[uuid.UUID | None] = mapped_column(
        UUID(as_uuid=True), ForeignKey("products.id"), index=True
    )
    crude_product_id: Mapped[uuid.UUID | None] = mapped_column(
        UUID(as_uuid=True), ForeignKey("crude_products.id"), index=True
    )
    material_id: Mapped[uuid.UUID | None] = mapped_column(
        UUID(as_uuid=True), ForeignKey("materials.id"), index=True
    )
    quantity: Mapped[Decimal] = mapped_column(Numeric(18, 4), nullable=False, default=0, comment="在庫数量")
    unit: Mapped[str] = mapped_column(String(20), nullable=False, default="個")
    standard_unit_price: Mapped[Decimal] = mapped_column(
        Numeric(18, 4), nullable=False, default=0, comment="標準単価（StandardCost等から取得）"
    )
    valuation_amount: Mapped[Decimal] = mapped_column(
        Numeric(18, 4), nullable=False, default=0, comment="評価金額 = quantity × standard_unit_price"
    )
    source_system: Mapped[SourceSystem] = mapped_column(
        Enum(SourceSystem), nullable=False, default=SourceSystem.manual
    )
    notes: Mapped[str | None] = mapped_column(Text)

    period: Mapped[FiscalPeriod] = relationship("FiscalPeriod", lazy="selectin")
    product: Mapped[Product | None] = relationship("Product", lazy="selectin")
    crude_product: Mapped[CrudeProduct | None] = relationship("CrudeProduct", lazy="selectin")
    material: Mapped["Material | None"] = relationship("Material", lazy="selectin")


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
