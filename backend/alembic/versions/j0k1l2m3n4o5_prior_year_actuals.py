"""prior_year_actuals テーブル新設

Revision ID: j0k1l2m3n4o5
Revises: i9j0k1l2m3n4
Create Date: 2026-05-19 12:00:00.000000

F-01 昨年実績インポートのデータ保持先。
30SC製品rev1.xlsx 「5.製品」シート由来の 38期全体の製品別年間SC原価フローを格納。

主要6項目 (期首/当期製造仕入/振替/売上原価/外注支給/期末) は数量・単価・原価の
3列セットで個別カラム化。振替系7項目 (販促費DM/販促費/試験研究費/接待交際費/
寄付金/広告宣伝費/在庫調整) は transfer_items JSONB に集約。
"""
from typing import Sequence, Union

import sqlalchemy as sa
from alembic import op
from sqlalchemy.dialects import postgresql


revision: str = "j0k1l2m3n4o5"
down_revision: str = "i9j0k1l2m3n4"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.create_table(
        "prior_year_actuals",
        sa.Column(
            "id",
            postgresql.UUID(as_uuid=True),
            primary_key=True,
            server_default=sa.text("gen_random_uuid()"),
        ),
        sa.Column("fiscal_year", sa.Integer(), nullable=False, comment="会計年度(38=第38期)"),
        sa.Column(
            "category",
            sa.String(length=20),
            nullable=True,
            comment="製造/仕入/製造振替/AB",
        ),
        sa.Column("product_code", sa.String(length=50), nullable=False),
        sa.Column("product_name", sa.String(length=200), nullable=True),
        sa.Column(
            "product_id",
            postgresql.UUID(as_uuid=True),
            sa.ForeignKey("products.id"),
            nullable=True,
            comment="マスタ名寄せできた場合のみ設定",
        ),

        # 期首商品棚卸高
        sa.Column("opening_qty", sa.Numeric(18, 4), nullable=False, server_default="0"),
        sa.Column("opening_unit_price", sa.Numeric(18, 6), nullable=False, server_default="0"),
        sa.Column("opening_cost", sa.Numeric(18, 2), nullable=False, server_default="0"),

        # 当期商品製造･仕入原価
        sa.Column("manufacturing_qty", sa.Numeric(18, 4), nullable=False, server_default="0"),
        sa.Column("manufacturing_unit_price", sa.Numeric(18, 6), nullable=False, server_default="0"),
        sa.Column("manufacturing_cost", sa.Numeric(18, 2), nullable=False, server_default="0"),

        # 振替
        sa.Column("transfer_qty", sa.Numeric(18, 4), nullable=False, server_default="0"),
        sa.Column("transfer_unit_price", sa.Numeric(18, 6), nullable=False, server_default="0"),
        sa.Column("transfer_cost", sa.Numeric(18, 2), nullable=False, server_default="0"),

        # 当期商品売上原価
        sa.Column("cogs_qty", sa.Numeric(18, 4), nullable=False, server_default="0"),
        sa.Column("cogs_unit_price", sa.Numeric(18, 6), nullable=False, server_default="0"),
        sa.Column("cogs_cost", sa.Numeric(18, 2), nullable=False, server_default="0"),

        # 外注支給分
        sa.Column("outsource_supply_qty", sa.Numeric(18, 4), nullable=False, server_default="0"),
        sa.Column("outsource_supply_unit_price", sa.Numeric(18, 6), nullable=False, server_default="0"),
        sa.Column("outsource_supply_cost", sa.Numeric(18, 2), nullable=False, server_default="0"),

        # 期末商品棚卸高
        sa.Column("closing_qty", sa.Numeric(18, 4), nullable=False, server_default="0"),
        sa.Column("closing_unit_price", sa.Numeric(18, 6), nullable=False, server_default="0"),
        sa.Column("closing_cost", sa.Numeric(18, 2), nullable=False, server_default="0"),

        # 振替系7項目 (販促費DM/販促費/試験研究費/接待交際費/寄付金/広告宣伝費/在庫調整)
        sa.Column(
            "transfer_items",
            postgresql.JSONB,
            nullable=False,
            server_default=sa.text("'{}'::jsonb"),
            comment="振替系項目 {key: {qty, cost}}",
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
        sa.UniqueConstraint("fiscal_year", "product_code", name="uq_prior_year_actual_year_code"),
    )
    op.create_index(
        "ix_prior_year_actuals_fiscal_year",
        "prior_year_actuals",
        ["fiscal_year"],
    )
    op.create_index(
        "ix_prior_year_actuals_product_code",
        "prior_year_actuals",
        ["product_code"],
    )
    op.create_index(
        "ix_prior_year_actuals_product_id",
        "prior_year_actuals",
        ["product_id"],
    )


def downgrade() -> None:
    op.drop_index("ix_prior_year_actuals_product_id", table_name="prior_year_actuals")
    op.drop_index("ix_prior_year_actuals_product_code", table_name="prior_year_actuals")
    op.drop_index("ix_prior_year_actuals_fiscal_year", table_name="prior_year_actuals")
    op.drop_table("prior_year_actuals")
