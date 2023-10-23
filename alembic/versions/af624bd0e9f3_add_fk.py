"""add fk

Revision ID: af624bd0e9f3
Revises: 99b3cf2234c7
Create Date: 2023-10-23 12:16:45.405977

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = 'af624bd0e9f3'
down_revision: Union[str, None] = '99b3cf2234c7'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.add_column("postsd",sa.Column('owner_id',sa.Integer,nullable=False))
    op.create_foreign_key('post_user_fk',source_table='postsd',referent_table='usersd'
                          ,local_cols=['owner_id'],remote_cols=['id'],ondelete="CASCADE")


def downgrade() -> None:
    op.drop_constraint('post_user_fk',table_name='postsd')
    op.drop_column('postsd','owner_id')
