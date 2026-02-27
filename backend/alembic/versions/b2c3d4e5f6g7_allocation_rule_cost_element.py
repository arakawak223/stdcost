"""allocation_rule: Add cost_element and priority columns

Revision ID: b2c3d4e5f6g7
Revises: a1b2c3d4e5f6
Create Date: 2026-02-27 12:00:00.000000

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa

# revision identifiers, used by Alembic.
revision: str = 'b2c3d4e5f6g7'
down_revision: Union[str, None] = 'a1b2c3d4e5f6'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.add_column('allocation_rules',
                  sa.Column('cost_element', sa.String(30), nullable=True,
                            comment='対象原価要素(labor/overhead/outsourcing)。NULLは全要素に適用'))
    op.add_column('allocation_rules',
                  sa.Column('priority', sa.Integer(), nullable=False, server_default='0',
                            comment='優先度（大きい方が優先）'))
    op.create_index('ix_allocation_rules_cost_element', 'allocation_rules', ['cost_element'])


def downgrade() -> None:
    op.drop_index('ix_allocation_rules_cost_element', table_name='allocation_rules')
    op.drop_column('allocation_rules', 'priority')
    op.drop_column('allocation_rules', 'cost_element')
