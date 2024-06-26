"""add users

Revision ID: e6296e12d3bd
Revises: a7d75acdd9a3
Create Date: 2024-05-26 07:46:54.113036

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = 'e6296e12d3bd'
down_revision: Union[str, None] = 'a7d75acdd9a3'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # ### commands auto generated by Alembic - please adjust! ###
    op.create_table('users',
    sa.Column('id', sa.Integer(), nullable=False),
    sa.Column('username', sa.String(length=50), nullable=True),
    sa.Column('email', sa.String(length=250), nullable=False),
    sa.Column('password', sa.String(length=255), nullable=False),
    sa.Column('crated_at', sa.DateTime(), nullable=True),
    sa.Column('refresh_token', sa.String(length=255), nullable=True),
    sa.PrimaryKeyConstraint('id'),
    sa.UniqueConstraint('email')
    )
    op.add_column('contacts', sa.Column('created_at', sa.DateTime(), nullable=True))
    op.add_column('contacts', sa.Column('update_at', sa.DateTime(), nullable=True))
    op.add_column('contacts', sa.Column('owner_id', sa.Integer(), nullable=True))
    op.create_foreign_key(None, 'contacts', 'users', ['owner_id'], ['id'])
    # ### end Alembic commands ###


def downgrade() -> None:
    # ### commands auto generated by Alembic - please adjust! ###
    op.drop_constraint(None, 'contacts', type_='foreignkey')
    op.drop_column('contacts', 'owner_id')
    op.drop_column('contacts', 'update_at')
    op.drop_column('contacts', 'created_at')
    op.drop_table('users')
    # ### end Alembic commands ###
