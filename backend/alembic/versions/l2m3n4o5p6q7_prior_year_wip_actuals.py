"""prior_year_wip_actuals テーブル新設

Revision ID: l2m3n4o5p6q7
Revises: k1l2m3n4o5p6
Create Date: 2026-06-10 10:00:00.000000

F-01 横展開: 20 SC仕掛品.xlsx 「仕掛品SC明細」シート由来の
38期 仕掛品(製造課)別 年間SC原価フローを格納。

主要6項目 (期首棚卸/原材料/労務費/経費/前工程費/期末棚卸) は数量・原価の
2列セットで個別カラム化。その他7項目 (完成品/研究費/販促費/廃棄処分/
次工程へ/製造部生産分/在庫調整) は cost_items JSONB に集約。
識別キーは 種類(wip_code) を fiscal_year と組み合わせて UNIQUE。
"""
from typing import Sequence, Union

import sqlalchemy as sa
from alembic import op
from sqlalchemy.dialects import postgresql


revision: str = "l2m3n4o5p6q7"
down_revision: str = "k1l2m3n4o5p6"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.create_table(
        "prior_year_wip_actuals",
        sa.Column(
            "id",
            postgresql.UUID(as_uuid=True),
            primary_key=True,
            server_default=sa.text("gen_random_uuid()"),
        ),
        sa.Column("fiscal_year", sa.Integer(), nullable=False, comment="会計年度(38=第38期)"),
        sa.Column("wip_code", sa.String(length=50), nullable=False, comment="種類 (例: 13R)"),
        sa.Column("production_year", sa.String(length=20), nullable=True, comment="仕込年度 (例: S62/H1)"),
        sa.Column("batch_no", sa.String(length=20), nullable=True, comment="番手"),
        sa.Column("nayose", sa.String(length=50), nullable=True, comment="名寄 (原液グループ 例: R/G)"),
        sa.Column("sc_unit_price", sa.Numeric(18, 6), nullable=False, server_default="0", comment="仕掛品SC単価"),

        # 期首棚卸
        sa.Column("opening_qty", sa.Numeric(18, 4), nullable=False, server_default="0"),
        sa.Column("opening_cost", sa.Numeric(18, 2), nullable=False, server_default="0"),
        # 原材料
        sa.Column("material_qty", sa.Numeric(18, 4), nullable=False, server_default="0"),
        sa.Column("material_cost", sa.Numeric(18, 2), nullable=False, server_default="0"),
        # 労務費
        sa.Column("labor_qty", sa.Numeric(18, 4), nullable=False, server_default="0"),
        sa.Column("labor_cost", sa.Numeric(18, 2), nullable=False, server_default="0"),
        # 経費
        sa.Column("expense_qty", sa.Numeric(18, 4), nullable=False, server_default="0"),
        sa.Column("expense_cost", sa.Numeric(18, 2), nullable=False, server_default="0"),
        # 前工程費
        sa.Column("pre_process_qty", sa.Numeric(18, 4), nullable=False, server_default="0"),
        sa.Column("pre_process_cost", sa.Numeric(18, 2), nullable=False, server_default="0"),
        # 期末棚卸
        sa.Column("closing_qty", sa.Numeric(18, 4), nullable=False, server_default="0"),
        sa.Column("closing_cost", sa.Numeric(18, 2), nullable=False, server_default="0"),

        # その他7項目 (完成品/研究費/販促費/廃棄処分/次工程へ/製造部生産分/在庫調整)
        sa.Column(
            "cost_items",
            postgresql.JSONB,
            nullable=False,
            server_default=sa.text("'{}'::jsonb"),
            comment="その他原価項目 {key: {label, qty, cost}}",
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
            "fiscal_year", "wip_code", name="uq_prior_year_wip_actual_year_code"
        ),
    )
    op.create_index(
        "ix_prior_year_wip_actuals_fiscal_year",
        "prior_year_wip_actuals",
        ["fiscal_year"],
    )
    op.create_index(
        "ix_prior_year_wip_actuals_wip_code",
        "prior_year_wip_actuals",
        ["wip_code"],
    )
    op.create_index(
        "ix_prior_year_wip_actuals_nayose",
        "prior_year_wip_actuals",
        ["nayose"],
    )


def downgrade() -> None:
    op.drop_index("ix_prior_year_wip_actuals_nayose", table_name="prior_year_wip_actuals")
    op.drop_index("ix_prior_year_wip_actuals_wip_code", table_name="prior_year_wip_actuals")
    op.drop_index("ix_prior_year_wip_actuals_fiscal_year", table_name="prior_year_wip_actuals")
    op.drop_table("prior_year_wip_actuals")
