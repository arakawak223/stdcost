"""products.sc_consolidation_key + wip_standard_costs

Revision ID: h8i9j0k1l2m3
Revises: g7h8i9j0k1l2
Create Date: 2026-05-14 12:00:00.000000

Changes:
  1. products に sc_consolidation_key カラム追加
     - 半製品(仕掛品)のSC単価計算用の名寄キー
       (B/BM/FB/G/GP/LPA/MP/O/P/PE/PX/PXA/RX/T/X/XC 等 + 「その他」)。
     - 直接マッチ16品目 + 「その他」マッピング36品目 = 52品目をカバー。
     - SC単価は wip_standard_costs テーブルで期別管理する。
  2. wip_standard_costs テーブル新設
     - 仕掛品(半製品)の標準単価を「名寄せキー × 期間」で管理。
     - 内訳: 前工程費・原材料費・労務費・経費。
     - 単価 unit_cost = 前工程費 + 原材料費 + 労務費 + 経費 (基本¥30固定)。
     - データソース: `docs/reference/決算用SC仕掛品.xlsx`
       「仕掛品標準単価一覧表（貼付）」シート 38件。
"""
from typing import Sequence, Union

import sqlalchemy as sa
from alembic import op
from sqlalchemy.dialects import postgresql


revision: str = "h8i9j0k1l2m3"
down_revision: str = "g7h8i9j0k1l2"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # --- 1. products.sc_consolidation_key 追加 ---
    op.add_column(
        "products",
        sa.Column(
            "sc_consolidation_key",
            sa.String(length=50),
            nullable=True,
            comment="SC計算上の名寄せキー(B/BM/FB/G/GP/MP/O/P等)。半製品の単価集約用。",
        ),
    )
    op.create_index(
        "ix_products_sc_consolidation_key",
        "products",
        ["sc_consolidation_key"],
    )

    # --- 2. wip_standard_costs テーブル作成 ---
    op.create_table(
        "wip_standard_costs",
        sa.Column(
            "id",
            postgresql.UUID(as_uuid=True),
            primary_key=True,
            server_default=sa.text("gen_random_uuid()"),
        ),
        sa.Column(
            "consolidation_key",
            sa.String(length=50),
            nullable=False,
            comment="名寄せキー(B/BM/FB/G/GP/MP/O/P等)",
        ),
        sa.Column(
            "period_id",
            postgresql.UUID(as_uuid=True),
            sa.ForeignKey("fiscal_periods.id"),
            nullable=False,
        ),
        sa.Column(
            "unit_cost",
            sa.Numeric(precision=12, scale=4),
            nullable=False,
            comment="SC単価合計(¥/kg) = 前工程費+原材料費+労務費+経費",
        ),
        sa.Column(
            "pre_process_cost",
            sa.Numeric(precision=12, scale=4),
            nullable=False,
            server_default="0",
            comment="前工程費(¥/kg)",
        ),
        sa.Column(
            "material_cost",
            sa.Numeric(precision=12, scale=4),
            nullable=False,
            server_default="0",
            comment="原材料費(¥/kg)",
        ),
        sa.Column(
            "labor_cost",
            sa.Numeric(precision=12, scale=4),
            nullable=False,
            server_default="0",
            comment="労務費(¥/kg)",
        ),
        sa.Column(
            "expense_cost",
            sa.Numeric(precision=12, scale=4),
            nullable=False,
            server_default="0",
            comment="経費(¥/kg)",
        ),
        sa.Column("effective_date", sa.Date(), nullable=True, comment="適用開始日(参考)"),
        sa.Column("notes", sa.Text(), nullable=True),
        sa.Column(
            "created_at",
            sa.DateTime(timezone=True),
            server_default=sa.func.now(),
            nullable=False,
        ),
        sa.Column(
            "updated_at",
            sa.DateTime(timezone=True),
            server_default=sa.func.now(),
            nullable=False,
        ),
        sa.UniqueConstraint(
            "consolidation_key",
            "period_id",
            name="uq_wip_std_cost_key_period",
        ),
    )
    op.create_index(
        "ix_wip_standard_costs_period_id",
        "wip_standard_costs",
        ["period_id"],
    )
    op.create_index(
        "ix_wip_standard_costs_consolidation_key",
        "wip_standard_costs",
        ["consolidation_key"],
    )


def downgrade() -> None:
    op.drop_index(
        "ix_wip_standard_costs_consolidation_key",
        table_name="wip_standard_costs",
    )
    op.drop_index(
        "ix_wip_standard_costs_period_id",
        table_name="wip_standard_costs",
    )
    op.drop_table("wip_standard_costs")
    op.drop_index("ix_products_sc_consolidation_key", table_name="products")
    op.drop_column("products", "sc_consolidation_key")
