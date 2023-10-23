"""what in the world

Revision ID: d3d5bd671cef
Revises: a93a69e4a975
Create Date: 2023-10-23 11:29:19.725349

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = 'd3d5bd671cef'
down_revision: Union[str, None] = None
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.create_table("block", sa.Column("bklock", sa.Integer(), nullable=True))

def downgrade() -> None:
    op.drop_table("block")
