"""sc_consolidation_key + material_standard_costs

Revision ID: g7h8i9j0k1l2
Revises: f6g7h8i9j0k1
Create Date: 2026-05-11 06:30:00.000000

Changes:
  1. crude_products に sc_consolidation_key カラム追加
     - SC計算用の名寄キー(R/HI/Rri/RB/plant 等)。crude_type と独立した
       SC上の集約単位(決算用SC仕掛品.xlsx「仕掛品SC明細」D列「名寄」相当)。
  2. material_standard_costs テーブル新設
     - 原材料の標準単価を期別管理。materials.standard_unit_price は
       「最新スナップショット用キャッシュ」として残置(段階的廃止)。
  3. 初期データ:
     - crude_products.sc_consolidation_key を crude_type で初期化
       (後段の補完スクリプトで精緻化)
     - 現存の materials.standard_unit_price>0 を 39期8か月目(2026年1月)に
       material_standard_costs として転記
"""
from typing import Sequence, Union

import sqlalchemy as sa
from alembic import op
from sqlalchemy.dialects import postgresql


revision: str = "g7h8i9j0k1l2"
down_revision: str = "f6g7h8i9j0k1"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # --- 1. crude_products.sc_consolidation_key 追加 ---
    op.add_column(
        "crude_products",
        sa.Column(
            "sc_consolidation_key",
            sa.String(length=20),
            nullable=True,
            comment="SC計算上の名寄せキー(R/HI/Rri/plant等)。crude_typeと独立。",
        ),
    )
    op.create_index(
        "ix_crude_products_sc_consolidation_key",
        "crude_products",
        ["sc_consolidation_key"],
    )

    # --- 2. material_standard_costs テーブル作成 ---
    op.create_table(
        "material_standard_costs",
        sa.Column("id", postgresql.UUID(as_uuid=True), primary_key=True, server_default=sa.text("gen_random_uuid()")),
        sa.Column("material_id", postgresql.UUID(as_uuid=True), sa.ForeignKey("materials.id", ondelete="CASCADE"), nullable=False),
        sa.Column("period_id", postgresql.UUID(as_uuid=True), sa.ForeignKey("fiscal_periods.id"), nullable=False),
        sa.Column("unit_cost", sa.Numeric(precision=12, scale=4), nullable=False),
        sa.Column("effective_date", sa.Date(), nullable=True),
        sa.Column("notes", sa.Text(), nullable=True),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
        sa.Column("updated_at", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
        sa.UniqueConstraint("material_id", "period_id", name="uq_material_std_cost_material_period"),
    )
    op.create_index("ix_material_standard_costs_period_id", "material_standard_costs", ["period_id"])
    op.create_index("ix_material_standard_costs_material_id", "material_standard_costs", ["material_id"])

    # --- 3. データ補完: sc_consolidation_key 初期値 = crude_type ---
    op.execute(
        """
        UPDATE crude_products
           SET sc_consolidation_key = crude_type::text
         WHERE sc_consolidation_key IS NULL;
        """
    )

    # --- 4. データ補完: materials.standard_unit_price > 0 を
    #        39期8か月目(2026-01-01開始) の material_standard_costs に転記 ---
    op.execute(
        """
        INSERT INTO material_standard_costs (material_id, period_id, unit_cost, effective_date, notes)
        SELECT
            m.id,
            fp.id,
            m.standard_unit_price,
            fp.start_date,
            'migration g7h8i9j0k1l2: materials.standard_unit_price から転記'
          FROM materials m
         CROSS JOIN fiscal_periods fp
         WHERE fp.year = 39 AND fp.month = 8
           AND m.standard_unit_price > 0
        ON CONFLICT (material_id, period_id) DO NOTHING;
        """
    )


def downgrade() -> None:
    op.drop_index("ix_material_standard_costs_material_id", table_name="material_standard_costs")
    op.drop_index("ix_material_standard_costs_period_id", table_name="material_standard_costs")
    op.drop_table("material_standard_costs")
    op.drop_index("ix_crude_products_sc_consolidation_key", table_name="crude_products")
    op.drop_column("crude_products", "sc_consolidation_key")
