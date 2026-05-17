"""processes + crude_product_process_routes + allocation_basis.actual_quantity

Revision ID: i9j0k1l2m3n4
Revises: h8i9j0k1l2m3
Create Date: 2026-05-17 12:00:00.000000

Changes:
  1. processes テーブル新設 (8工程の発酵プロセスマスタ)
  2. crude_product_process_routes テーブル新設 (原液×工程の実績ルート)
  3. allocationbasis enum に 'actual_quantity' を追加 (工程単位配賦用)
"""
from typing import Sequence, Union

import sqlalchemy as sa
from alembic import op
from sqlalchemy.dialects import postgresql


revision: str = "i9j0k1l2m3n4"
down_revision: str = "h8i9j0k1l2m3"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # --- 1. processes テーブル ---
    op.create_table(
        "processes",
        sa.Column(
            "id",
            postgresql.UUID(as_uuid=True),
            primary_key=True,
            server_default=sa.text("gen_random_uuid()"),
        ),
        sa.Column("code", sa.String(length=20), nullable=False),
        sa.Column("name", sa.String(length=100), nullable=False),
        sa.Column(
            "sort_order",
            sa.Integer(),
            nullable=False,
            server_default="0",
            comment="原液製造フロー上の標準順序(1:仕込→...→7:充填)",
        ),
        sa.Column("is_active", sa.Boolean(), nullable=False, server_default=sa.true()),
        sa.Column("notes", sa.Text(), nullable=True),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
        sa.Column("updated_at", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
        sa.UniqueConstraint("code", name="uq_processes_code"),
    )
    op.create_index("ix_processes_code", "processes", ["code"])

    # --- 2. crude_product_process_routes テーブル ---
    op.create_table(
        "crude_product_process_routes",
        sa.Column(
            "id",
            postgresql.UUID(as_uuid=True),
            primary_key=True,
            server_default=sa.text("gen_random_uuid()"),
        ),
        sa.Column(
            "crude_product_id",
            postgresql.UUID(as_uuid=True),
            sa.ForeignKey("crude_products.id"),
            nullable=False,
        ),
        sa.Column(
            "process_id",
            postgresql.UUID(as_uuid=True),
            sa.ForeignKey("processes.id"),
            nullable=False,
        ),
        sa.Column(
            "period_id",
            postgresql.UUID(as_uuid=True),
            sa.ForeignKey("fiscal_periods.id"),
            nullable=False,
        ),
        sa.Column(
            "sequence_no",
            sa.Integer(),
            nullable=True,
            comment="この原液内での工程通過順序(1=最初の工程, 2=次の工程, ...)",
        ),
        sa.Column(
            "actual_quantity",
            sa.Numeric(precision=18, scale=4),
            nullable=False,
            server_default="0",
            comment="実績数量(主に原材料投入量・処理量、配賦基準量)",
        ),
        sa.Column(
            "actual_hours",
            sa.Numeric(precision=18, scale=4),
            nullable=True,
            comment="作業時間(分または時間、補助基準)",
        ),
        sa.Column("notes", sa.Text(), nullable=True),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
        sa.Column("updated_at", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
        sa.UniqueConstraint(
            "crude_product_id", "process_id", "period_id",
            name="uq_crude_process_period",
        ),
    )
    op.create_index(
        "ix_crude_product_process_routes_crude_product_id",
        "crude_product_process_routes",
        ["crude_product_id"],
    )
    op.create_index(
        "ix_crude_product_process_routes_process_id",
        "crude_product_process_routes",
        ["process_id"],
    )
    op.create_index(
        "ix_crude_product_process_routes_period_id",
        "crude_product_process_routes",
        ["period_id"],
    )

    # --- 3. allocationbasis enum に actual_quantity 追加 ---
    op.execute("ALTER TYPE allocationbasis ADD VALUE IF NOT EXISTS 'actual_quantity'")


def downgrade() -> None:
    # Note: PostgreSQLでは enum 値の削除は安全に行えないため、enumの値は残す
    op.drop_index(
        "ix_crude_product_process_routes_period_id",
        table_name="crude_product_process_routes",
    )
    op.drop_index(
        "ix_crude_product_process_routes_process_id",
        table_name="crude_product_process_routes",
    )
    op.drop_index(
        "ix_crude_product_process_routes_crude_product_id",
        table_name="crude_product_process_routes",
    )
    op.drop_table("crude_product_process_routes")
    op.drop_index("ix_processes_code", table_name="processes")
    op.drop_table("processes")
