"""crude_product_multistage - 原体マスタ多段階工程対応

Revision ID: c3d4e5f6g7h8
Revises: 46a61c9ae54a
Create Date: 2026-03-17 12:00:00.000000

Changes:
  1. CrudeProductType enum: 新しい工程タイプ追加 (R1,R2,R3,Rri,RB,Rma,Rshi,RG,RGI,FEB,HIA,HIB,P,MP,GP,LPA,PE,T,RX)
  2. BomType enum: crude_product_process 追加（原体→原体の多段工程）
  3. crude_products table: process_stage, parent_crude_product_id カラム追加
"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects.postgresql import UUID


# revision identifiers, used by Alembic.
revision: str = 'c3d4e5f6g7h8'
down_revision: str = '46a61c9ae54a'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # PostgreSQL ALTER TYPE ... ADD VALUE cannot run inside a transaction
    # Use autocommit for enum changes
    op.execute("COMMIT")

    # 1. Expand CrudeProductType enum
    new_crude_types = [
        "R1", "R2", "R3", "Rri", "RB", "Rma", "Rshi", "RG", "RGI", "FEB",
        "HIA", "HIB", "HIR", "HIBkai",
        "B", "GA", "GB", "O", "X", "XC", "BM", "FB",
        "P", "PX", "PXA", "MP", "GP", "LPA", "PE", "T", "RX", "plant",
    ]
    for val in new_crude_types:
        op.execute(f"ALTER TYPE crudeproducttype ADD VALUE IF NOT EXISTS '{val}'")

    # 2. Add crude_product_process to BomType enum
    op.execute("ALTER TYPE bomtype ADD VALUE IF NOT EXISTS 'crude_product_process'")

    # Re-enter transaction for DDL
    op.execute("BEGIN")

    # 3. Add new columns to crude_products
    op.add_column("crude_products", sa.Column(
        "process_stage", sa.Integer(), nullable=True,
        comment="工程段階（1=一次仕込み, 2=二次, ... DAGのトポロジカル順序）"
    ))
    op.add_column("crude_products", sa.Column(
        "parent_crude_product_id",
        UUID(as_uuid=True),
        sa.ForeignKey("crude_products.id"),
        nullable=True,
        comment="主要な前工程原体ID（UIツリー表示用）"
    ))


def downgrade() -> None:
    op.drop_column("crude_products", "parent_crude_product_id")
    op.drop_column("crude_products", "process_stage")
    # Note: PostgreSQL does not support removing enum values directly.
    # The enum expansion is not reversible without recreating the type.
