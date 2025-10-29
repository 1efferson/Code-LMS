"""empty message

Revision ID: 1d3fd99b3d49
Revises: c2e13ce54a31
Create Date: 2025-10-25 08:03:24.252679

"""
from alembic import op
import sqlalchemy as sa
from sqlalchemy.sql import table, column 
from sqlalchemy.sql import expression as sa_expression


# revision identifiers, used by Alembic.
revision = '1d3fd99b3d49'
down_revision = 'c2e13ce54a31'
branch_labels = None
depends_on = None


def upgrade():
    # Define table object for op.execute to safely run SQL update
    user_table = table('user', column('is_admin', sa.Boolean))

    # STEP 1: Update existing rows where is_admin is NULL to False.
    # This prevents the NOT NULL constraint violation on existing data.
    op.execute(
        user_table.update().where(user_table.c.is_admin.is_(None)).values(is_admin=sa_expression.literal(False))
    )
    
    # STEP 2: Now alter the column to enforce the NOT NULL constraint (nullable=False)
    with op.batch_alter_table('user', schema=None) as batch_op:
        batch_op.alter_column('is_admin',
               existing_type=sa.BOOLEAN(),
               nullable=False)


def downgrade():
    # Reverts the column constraint to allow NULL values again
    with op.batch_alter_table('user', schema=None) as batch_op:
        batch_op.alter_column('is_admin',
               existing_type=sa.BOOLEAN(),
               nullable=True)