"""add_budget_model

Revision ID: a1b2c3d4e5f6
Revises: e5d40eef8a5e
Create Date: 2026-08-25 13:25:00.000000

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = 'a1b2c3d4e5f6'
down_revision = 'e5d40eef8a5e'
branch_labels = None
depends_on = None


def upgrade():
    op.create_table('budget',
    sa.Column('id', sa.Integer(), nullable=False),
    sa.Column('name', sa.String(length=100), nullable=False),
    sa.Column('description', sa.Text(), nullable=True),
    sa.Column('fiscal_year', sa.String(length=10), nullable=False),
    sa.Column('total_amount', sa.Integer(), nullable=False, server_default='0'),
    sa.Column('status', sa.String(length=20), nullable=False, server_default='Draft'),
    sa.Column('approved_by', sa.Integer(), nullable=True),
    sa.Column('approved_at', sa.DateTime(timezone=True), nullable=True),
    sa.Column('created_by', sa.Integer(), nullable=True),
    sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=True),
    sa.Column('updated_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=True),
    sa.ForeignKeyConstraint(['approved_by'], ['user.id'], ),
    sa.ForeignKeyConstraint(['created_by'], ['user.id'], ),
    sa.PrimaryKeyConstraint('id')
    )
    op.create_table('budget_item',
    sa.Column('id', sa.Integer(), nullable=False),
    sa.Column('budget_id', sa.Integer(), nullable=False),
    sa.Column('category', sa.String(length=100), nullable=False),
    sa.Column('description', sa.Text(), nullable=True),
    sa.Column('amount', sa.Integer(), nullable=False),
    sa.Column('item_type', sa.String(length=20), nullable=False, server_default='Expense'),
    sa.ForeignKeyConstraint(['budget_id'], ['budget.id'], ),
    sa.PrimaryKeyConstraint('id')
    )


def downgrade():
    op.drop_table('budget_item')
    op.drop_table('budget')
