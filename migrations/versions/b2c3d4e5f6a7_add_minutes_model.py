"""add_minutes_model

Revision ID: b2c3d4e5f6a7
Revises: a1b2c3d4e5f6
Create Date: 2026-08-25 13:25:00.000000

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = 'b2c3d4e5f6a7'
down_revision = 'a1b2c3d4e5f6'
branch_labels = None
depends_on = None


def upgrade():
    op.create_table('minutes',
    sa.Column('id', sa.Integer(), nullable=False),
    sa.Column('title', sa.String(length=150), nullable=False),
    sa.Column('meeting_type', sa.String(length=50), nullable=False, server_default='General'),
    sa.Column('meeting_date', sa.Date(), nullable=False),
    sa.Column('location', sa.String(length=150), nullable=True),
    sa.Column('agenda', sa.Text(), nullable=True),
    sa.Column('discussion', sa.Text(), nullable=True),
    sa.Column('decisions', sa.Text(), nullable=True),
    sa.Column('action_items', sa.Text(), nullable=True),
    sa.Column('next_meeting_date', sa.Date(), nullable=True),
    sa.Column('attendees', sa.Text(), nullable=True),
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


def downgrade():
    op.drop_table('minutes')
