"""prior_year_material_actuals テーブル新設

Revision ID: k1l2m3n4o5p6
Revises: j0k1l2m3n4o5
Create Date: 2026-06-10 09:00:00.000000

F-01 横展開: 10 SC原材料.xlsx 「原材料SC明細」シート由来の
38期 原材料別 年間SC原価フローを格納。

主要4項目 (期首棚卸/当期仕入高/当期投入高/期末棚卸) は数量・原価の
2列セットで個別カラム化。調整系7項目 (検査・分析/試用/返品/ロス分/
廃棄処分/在庫調整/その他調整) は adjustment_items JSONB に集約。
SC単価は原料単位の単一カラム (sc_unit_price)。
"""
from typing import Sequence, Union

import sqlalchemy as sa
from alembic import op
from sqlalchemy.dialects import postgresql


revision: str = "k1l2m3n4o5p6"
down_revision: str = "j0k1l2m3n4o5"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.create_table(
        "prior_year_material_actuals",
        sa.Column(
            "id",
            postgresql.UUID(as_uuid=True),
            primary_key=True,
            server_default=sa.text("gen_random_uuid()"),
        ),
        sa.Column("fiscal_year", sa.Integer(), nullable=False, comment="会計年度(38=第38期)"),
        sa.Column("material_code", sa.String(length=50), nullable=False),
        sa.Column("material_name", sa.String(length=200), nullable=True),
        sa.Column(
            "material_id",
            postgresql.UUID(as_uuid=True),
            sa.ForeignKey("materials.id"),
            nullable=True,
            comment="マスタ名寄せできた場合のみ設定",
        ),
        sa.Column("sc_unit_price", sa.Numeric(18, 6), nullable=False, server_default="0", comment="原料SC単価"),
        sa.Column("unit", sa.String(length=20), nullable=True, comment="数量単位 (例: 数量(㎏))"),

        # 期首棚卸
        sa.Column("opening_qty", sa.Numeric(18, 4), nullable=False, server_default="0"),
        sa.Column("opening_cost", sa.Numeric(18, 2), nullable=False, server_default="0"),
        # 当期仕入高
        sa.Column("purchase_qty", sa.Numeric(18, 4), nullable=False, server_default="0"),
        sa.Column("purchase_cost", sa.Numeric(18, 2), nullable=False, server_default="0"),
        # 当期投入高
        sa.Column("input_qty", sa.Numeric(18, 4), nullable=False, server_default="0"),
        sa.Column("input_cost", sa.Numeric(18, 2), nullable=False, server_default="0"),
        # 期末棚卸
        sa.Column("closing_qty", sa.Numeric(18, 4), nullable=False, server_default="0"),
        sa.Column("closing_cost", sa.Numeric(18, 2), nullable=False, server_default="0"),

        # 調整系7項目 (検査・分析/試用/返品/ロス分/廃棄処分/在庫調整/その他調整)
        sa.Column(
            "adjustment_items",
            postgresql.JSONB,
            nullable=False,
            server_default=sa.text("'{}'::jsonb"),
            comment="調整系項目 {key: {label, qty, cost}}",
        ),

        sa.Column("source_file", sa.String(length=255), nullable=True),
        sa.Column("source_sheet", sa.String(length=100), nullable=True),
        sa.Column(
            "import_batch_id",
            postgresql.UUID(as_uuid=True),
            sa.ForeignKey("import_batches.id"),
            nullable=True,
        ),
        sa.Column("notes", sa.Text(), nullable=True),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
        sa.Column("updated_at", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
        sa.UniqueConstraint(
            "fiscal_year", "material_code", name="uq_prior_year_material_actual_year_code"
        ),
    )
    op.create_index(
        "ix_prior_year_material_actuals_fiscal_year",
        "prior_year_material_actuals",
        ["fiscal_year"],
    )
    op.create_index(
        "ix_prior_year_material_actuals_material_code",
        "prior_year_material_actuals",
        ["material_code"],
    )
    op.create_index(
        "ix_prior_year_material_actuals_material_id",
        "prior_year_material_actuals",
        ["material_id"],
    )


def downgrade() -> None:
    op.drop_index(
        "ix_prior_year_material_actuals_material_id",
        table_name="prior_year_material_actuals",
    )
    op.drop_index(
        "ix_prior_year_material_actuals_material_code",
        table_name="prior_year_material_actuals",
    )
    op.drop_index(
        "ix_prior_year_material_actuals_fiscal_year",
        table_name="prior_year_material_actuals",
    )
    op.drop_table("prior_year_material_actuals")
