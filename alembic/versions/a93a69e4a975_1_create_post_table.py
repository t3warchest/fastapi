"""1 create post table

Revision ID: a93a69e4a975
Revises: 
Create Date: 2023-10-23 11:15:46.447939

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = 'a93a69e4a975'
down_revision: Union[str, None] = None
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.create_table("test",sa.Column("blocvkl", sa.Integer(), nullable=False, primary_key=True),sa.Column("buster", sa.String(), nullable=False))
    


def downgrade() -> None:
    op.drop_table('postsd')
