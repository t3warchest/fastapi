"""add suer tbale

Revision ID: 99b3cf2234c7
Revises: 04ef67d0f3f5
Create Date: 2023-10-23 11:55:29.555678

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = '99b3cf2234c7'
down_revision: Union[str, None] = '04ef67d0f3f5'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.create_table('usersd',sa.Column('id', sa.Integer(), nullable=False), 
                    sa.Column('email', sa.String(), nullable=False), 
                    sa.Column("password", sa.String(), nullable=False), 
                    sa.Column('created _at', sa.TIMESTAMP(timezone=True),
                              server_default=sa.text('now()'), nullable=False),
                    sa.PrimaryKeyConstraint('id'), sa.UniqueConstraint('email'))


def downgrade() -> None:
    op.drop_table('usersd')
