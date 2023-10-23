"""add content column

Revision ID: 04ef67d0f3f5
Revises: d3d5bd671cef
Create Date: 2023-10-23 11:36:54.407765

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = '04ef67d0f3f5'
down_revision: Union[str, None] = 'a93a69e4a975'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.add_column("postsd",sa.Column('content',sa.String,nullable=False))


def downgrade() -> None:
    op.drop_column("postsd",'content')
