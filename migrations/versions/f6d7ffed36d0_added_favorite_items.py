"""Added favorite items.

Revision ID: f6d7ffed36d0
Revises: 47af861cde66
Create Date: 2018-09-05 10:06:40.354967

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = 'f6d7ffed36d0'
down_revision = '47af861cde66'
branch_labels = None
depends_on = None


def upgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.add_column('item', sa.Column('favorite', sa.Boolean(), nullable=True))
    # ### end Alembic commands ###


def downgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.drop_column('item', 'favorite')
    # ### end Alembic commands ###