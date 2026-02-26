"""phase2_bom_budget: Add crude_product_id to bom_headers, create cost_budgets table

Revision ID: a1b2c3d4e5f6
Revises: bf93fb832bbb
Create Date: 2026-02-26 12:00:00.000000

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

# revision identifiers, used by Alembic.
revision: str = 'a1b2c3d4e5f6'
down_revision: Union[str, None] = 'bf93fb832bbb'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # --- BomHeader changes ---
    # Make product_id nullable
    op.alter_column('bom_headers', 'product_id',
                    existing_type=sa.UUID(),
                    nullable=True)

    # Add crude_product_id column
    op.add_column('bom_headers',
                  sa.Column('crude_product_id', sa.UUID(), nullable=True,
                            comment='Stage 1 BOM: 原体を出力する場合'))
    op.create_index(op.f('ix_bom_headers_crude_product_id'), 'bom_headers',
                    ['crude_product_id'], unique=False)
    op.create_foreign_key('fk_bom_headers_crude_product_id', 'bom_headers',
                          'crude_products', ['crude_product_id'], ['id'])

    # Add unique constraint for crude_product BOM
    op.create_unique_constraint('uq_bom_crude_type_date', 'bom_headers',
                                ['crude_product_id', 'bom_type', 'effective_date'])

    # --- New cost_budgets table ---
    op.create_table('cost_budgets',
        sa.Column('cost_center_id', sa.UUID(), nullable=False),
        sa.Column('period_id', sa.UUID(), nullable=False),
        sa.Column('labor_budget', sa.Numeric(precision=18, scale=4), nullable=False,
                  server_default='0', comment='労務費予算'),
        sa.Column('overhead_budget', sa.Numeric(precision=18, scale=4), nullable=False,
                  server_default='0', comment='経費予算'),
        sa.Column('outsourcing_budget', sa.Numeric(precision=18, scale=4), nullable=False,
                  server_default='0', comment='外注費予算'),
        sa.Column('notes', sa.Text(), nullable=True),
        sa.Column('id', sa.UUID(), nullable=False),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.text('now()'),
                  nullable=False),
        sa.Column('updated_at', sa.DateTime(timezone=True), server_default=sa.text('now()'),
                  nullable=False),
        sa.ForeignKeyConstraint(['cost_center_id'], ['cost_centers.id']),
        sa.ForeignKeyConstraint(['period_id'], ['fiscal_periods.id']),
        sa.PrimaryKeyConstraint('id'),
        sa.UniqueConstraint('cost_center_id', 'period_id', name='uq_cost_budget_cc_period'),
    )
    op.create_index(op.f('ix_cost_budgets_cost_center_id'), 'cost_budgets',
                    ['cost_center_id'], unique=False)
    op.create_index(op.f('ix_cost_budgets_period_id'), 'cost_budgets',
                    ['period_id'], unique=False)


def downgrade() -> None:
    op.drop_index(op.f('ix_cost_budgets_period_id'), table_name='cost_budgets')
    op.drop_index(op.f('ix_cost_budgets_cost_center_id'), table_name='cost_budgets')
    op.drop_table('cost_budgets')

    op.drop_constraint('uq_bom_crude_type_date', 'bom_headers', type_='unique')
    op.drop_constraint('fk_bom_headers_crude_product_id', 'bom_headers', type_='foreignkey')
    op.drop_index(op.f('ix_bom_headers_crude_product_id'), table_name='bom_headers')
    op.drop_column('bom_headers', 'crude_product_id')

    op.alter_column('bom_headers', 'product_id',
                    existing_type=sa.UUID(),
                    nullable=False)
