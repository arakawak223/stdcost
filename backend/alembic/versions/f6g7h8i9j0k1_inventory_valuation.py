"""inventory_valuation - 期末在庫評価テーブル追加

Revision ID: f6g7h8i9j0k1
Revises: e5f6g7h8i9j0
Create Date: 2026-04-29 00:30:00.000000

Changes:
  1. inventorycategory enum 追加
  2. inventory_valuations テーブル追加
     - period × warehouse × item_code の一意制約
     - product/crude_product/material への外部キー (NULLABLE、マスタ未登録対応)
     - quantity × standard_unit_price = valuation_amount を保持
"""
from typing import Sequence, Union

import sqlalchemy as sa
from alembic import op
from sqlalchemy.dialects import postgresql


revision: str = "f6g7h8i9j0k1"
down_revision: str = "e5f6g7h8i9j0"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


INVENTORY_CATEGORY_VALUES = (
    "product", "semi_finished", "crude_product",
    "raw_material", "sub_material", "merchandise", "other",
)


def upgrade() -> None:
    # --- 1. enum型作成 ---
    inventory_category = postgresql.ENUM(
        *INVENTORY_CATEGORY_VALUES, name="inventorycategory", create_type=False
    )
    inventory_category.create(op.get_bind(), checkfirst=True)

    # --- 2. inventory_valuations テーブル作成 ---
    op.create_table(
        "inventory_valuations",
        sa.Column("id", postgresql.UUID(as_uuid=True), primary_key=True),
        sa.Column("period_id", postgresql.UUID(as_uuid=True), sa.ForeignKey("fiscal_periods.id"), nullable=False),
        sa.Column("item_code", sa.String(30), nullable=False),
        sa.Column("item_name", sa.String(200), nullable=True),
        sa.Column("warehouse_name", sa.String(100), nullable=False),
        sa.Column(
            "category",
            postgresql.ENUM(*INVENTORY_CATEGORY_VALUES, name="inventorycategory", create_type=False),
            nullable=False,
        ),
        sa.Column("product_id", postgresql.UUID(as_uuid=True), sa.ForeignKey("products.id"), nullable=True),
        sa.Column("crude_product_id", postgresql.UUID(as_uuid=True), sa.ForeignKey("crude_products.id"), nullable=True),
        sa.Column("material_id", postgresql.UUID(as_uuid=True), sa.ForeignKey("materials.id"), nullable=True),
        sa.Column("quantity", sa.Numeric(18, 4), nullable=False, server_default="0"),
        sa.Column("unit", sa.String(20), nullable=False, server_default="個"),
        sa.Column("standard_unit_price", sa.Numeric(18, 4), nullable=False, server_default="0"),
        sa.Column("valuation_amount", sa.Numeric(18, 4), nullable=False, server_default="0"),
        sa.Column(
            "source_system",
            postgresql.ENUM(
                "geneki_db", "sc_system", "kanjyo_bugyo", "tsuhan21",
                "romu_db", "product_db", "manual",
                name="sourcesystem", create_type=False,
            ),
            nullable=False,
            server_default="manual",
        ),
        sa.Column("notes", sa.Text(), nullable=True),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
        sa.Column("updated_at", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
        sa.UniqueConstraint("item_code", "warehouse_name", "period_id", name="uq_inv_val_code_wh_period"),
    )
    op.create_index("ix_inventory_valuations_period_id", "inventory_valuations", ["period_id"])
    op.create_index("ix_inventory_valuations_item_code", "inventory_valuations", ["item_code"])
    op.create_index("ix_inventory_valuations_warehouse_name", "inventory_valuations", ["warehouse_name"])
    op.create_index("ix_inventory_valuations_category", "inventory_valuations", ["category"])
    op.create_index("ix_inventory_valuations_product_id", "inventory_valuations", ["product_id"])
    op.create_index("ix_inventory_valuations_crude_product_id", "inventory_valuations", ["crude_product_id"])
    op.create_index("ix_inventory_valuations_material_id", "inventory_valuations", ["material_id"])


def downgrade() -> None:
    op.drop_index("ix_inventory_valuations_material_id", table_name="inventory_valuations")
    op.drop_index("ix_inventory_valuations_crude_product_id", table_name="inventory_valuations")
    op.drop_index("ix_inventory_valuations_product_id", table_name="inventory_valuations")
    op.drop_index("ix_inventory_valuations_category", table_name="inventory_valuations")
    op.drop_index("ix_inventory_valuations_warehouse_name", table_name="inventory_valuations")
    op.drop_index("ix_inventory_valuations_item_code", table_name="inventory_valuations")
    op.drop_index("ix_inventory_valuations_period_id", table_name="inventory_valuations")
    op.drop_table("inventory_valuations")
    op.execute("DROP TYPE IF EXISTS inventorycategory")
