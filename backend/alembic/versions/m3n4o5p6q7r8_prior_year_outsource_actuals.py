"""prior_year_outsource_actuals テーブル新設

Revision ID: m3n4o5p6q7r8
Revises: l2m3n4o5p6q7
Create Date: 2026-06-10 11:00:00.000000

F-01 横展開: 31SC外注製品.xlsx 「標準原価_外注製品」シート由来の
38期 外注製品別 単価(38期実際/39期標準) + 数量・金額フローを格納。

主要4項目 (37期末=期首/生産/販売/38期末=期末) は数量・原価の2列セット。
その他10項目 (外注支給/製品内製へ/その他振替/販促DM/販促/試験研究費/交際費/
寄付金/広告宣伝費/在庫調整) は movements JSONB に集約。
単価は 38期実際 / 39期標準 の各 外注加工費/その他原価/外注製品原価。
識別キーは 商品コード(product_code, 99件一意)。
"""
from typing import Sequence, Union

import sqlalchemy as sa
from alembic import op
from sqlalchemy.dialects import postgresql


revision: str = "m3n4o5p6q7r8"
down_revision: str = "l2m3n4o5p6q7"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.create_table(
        "prior_year_outsource_actuals",
        sa.Column(
            "id",
            postgresql.UUID(as_uuid=True),
            primary_key=True,
            server_default=sa.text("gen_random_uuid()"),
        ),
        sa.Column("fiscal_year", sa.Integer(), nullable=False, comment="会計年度(38=第38期)"),
        sa.Column("product_code", sa.String(length=50), nullable=False),
        sa.Column("product_name", sa.String(length=200), nullable=True),
        sa.Column(
            "product_id",
            postgresql.UUID(as_uuid=True),
            sa.ForeignKey("products.id"),
            nullable=True,
            comment="マスタ名寄せできた場合のみ設定",
        ),
        sa.Column("section", sa.String(length=50), nullable=True, comment="区分 A.〜F."),
        sa.Column("contractor_code", sa.String(length=50), nullable=True, comment="外注先補助科目コード"),
        sa.Column("contractor_name", sa.String(length=200), nullable=True),
        sa.Column("supplied_material_code", sa.String(length=50), nullable=True, comment="支給原料の商品コード"),
        sa.Column("supplied_material_label", sa.String(length=100), nullable=True, comment="支給原料"),

        # 単価情報 (単位原価/個)
        sa.Column("actual_processing_cost", sa.Numeric(18, 6), nullable=False, server_default="0", comment="38期実際 外注加工費"),
        sa.Column("actual_other_cost", sa.Numeric(18, 6), nullable=False, server_default="0", comment="38期実際 その他原価"),
        sa.Column("actual_product_cost", sa.Numeric(18, 6), nullable=False, server_default="0", comment="38期実際 外注製品原価"),
        sa.Column("std_processing_cost", sa.Numeric(18, 6), nullable=False, server_default="0", comment="39期標準 外注加工費"),
        sa.Column("std_other_cost", sa.Numeric(18, 6), nullable=False, server_default="0", comment="39期標準 その他原価"),
        sa.Column("std_product_cost", sa.Numeric(18, 6), nullable=False, server_default="0", comment="39期標準 外注製品原価"),

        # 主要4項目 (数量=個 / 金額=円)
        sa.Column("opening_qty", sa.Numeric(18, 4), nullable=False, server_default="0", comment="37期末"),
        sa.Column("opening_cost", sa.Numeric(18, 2), nullable=False, server_default="0"),
        sa.Column("production_qty", sa.Numeric(18, 4), nullable=False, server_default="0", comment="生産"),
        sa.Column("production_cost", sa.Numeric(18, 2), nullable=False, server_default="0"),
        sa.Column("sales_qty", sa.Numeric(18, 4), nullable=False, server_default="0", comment="販売"),
        sa.Column("sales_cost", sa.Numeric(18, 2), nullable=False, server_default="0"),
        sa.Column("closing_qty", sa.Numeric(18, 4), nullable=False, server_default="0", comment="38期末"),
        sa.Column("closing_cost", sa.Numeric(18, 2), nullable=False, server_default="0"),

        # その他10項目 {key: {label, qty, cost}}
        sa.Column(
            "movements",
            postgresql.JSONB,
            nullable=False,
            server_default=sa.text("'{}'::jsonb"),
            comment="その他振替・販促等 {key: {label, qty, cost}}",
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
            "fiscal_year", "product_code", name="uq_prior_year_outsource_actual_year_code"
        ),
    )
    op.create_index(
        "ix_prior_year_outsource_actuals_fiscal_year",
        "prior_year_outsource_actuals",
        ["fiscal_year"],
    )
    op.create_index(
        "ix_prior_year_outsource_actuals_product_code",
        "prior_year_outsource_actuals",
        ["product_code"],
    )
    op.create_index(
        "ix_prior_year_outsource_actuals_product_id",
        "prior_year_outsource_actuals",
        ["product_id"],
    )


def downgrade() -> None:
    op.drop_index(
        "ix_prior_year_outsource_actuals_product_id",
        table_name="prior_year_outsource_actuals",
    )
    op.drop_index(
        "ix_prior_year_outsource_actuals_product_code",
        table_name="prior_year_outsource_actuals",
    )
    op.drop_index(
        "ix_prior_year_outsource_actuals_fiscal_year",
        table_name="prior_year_outsource_actuals",
    )
    op.drop_table("prior_year_outsource_actuals")
