"""prior_year_r_wip_components テーブル新設

Revision ID: n4o5p6q7r8s9
Revises: m3n4o5p6q7r8
Create Date: 2026-06-11 10:00:00.000000

F-01 横展開 (最終): R仕掛品 (原液系列 R1/R2/R3) の加重平均原価コンポーネントを格納。
  - 21-1 R仕掛品　原材料.xlsx 「R仕掛原材料費」シート → cost_component='material'
  - 21-2 R仕掛品　労務費.xlsx 「R仕掛品　労務費」シート → cost_component='labor'

両シートとも 34〜38期のロットを縦積みして加重平均単価を導出するクロス集計
ワークシート。各 R系列の **加重平均結果のみ** を 1レコードとして取り込む
(原材料=「加重平均」ラベル行、労務費=罫線囲み「□採用値」)。
識別キーは (fiscal_year, r_series, cost_component)。fiscal_year 単位 (38期)。
"""
from typing import Sequence, Union

import sqlalchemy as sa
from alembic import op
from sqlalchemy.dialects import postgresql


revision: str = "n4o5p6q7r8s9"
down_revision: str = "m3n4o5p6q7r8"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.create_table(
        "prior_year_r_wip_components",
        sa.Column(
            "id",
            postgresql.UUID(as_uuid=True),
            primary_key=True,
            server_default=sa.text("gen_random_uuid()"),
        ),
        sa.Column("fiscal_year", sa.Integer(), nullable=False, comment="会計年度(38=第38期)"),
        sa.Column("r_series", sa.String(length=10), nullable=False, comment="原液系列 (R1/R2/R3)"),
        sa.Column(
            "cost_component",
            sa.String(length=20),
            nullable=False,
            comment="原価コンポーネント (material=原材料費 / labor=労務費)",
        ),
        sa.Column("weighted_avg_qty", sa.Numeric(18, 4), nullable=False, server_default="0", comment="加重平均数量(KG)"),
        sa.Column("weighted_avg_amount", sa.Numeric(18, 2), nullable=False, server_default="0", comment="加重平均金額(円)"),
        sa.Column("weighted_avg_unit_price", sa.Numeric(18, 4), nullable=False, server_default="0", comment="加重平均単価(円/KG)"),
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
            "fiscal_year",
            "r_series",
            "cost_component",
            name="uq_prior_year_r_wip_component_key",
        ),
    )
    op.create_index(
        "ix_prior_year_r_wip_components_fiscal_year",
        "prior_year_r_wip_components",
        ["fiscal_year"],
    )


def downgrade() -> None:
    op.drop_index(
        "ix_prior_year_r_wip_components_fiscal_year",
        table_name="prior_year_r_wip_components",
    )
    op.drop_table("prior_year_r_wip_components")
