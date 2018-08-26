"""Made birthdate not nullable.

Revision ID: edea8eca3ae8
Revises: ec9c4deb0227
Create Date: 2018-08-26 17:16:28.122870

"""
from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import mysql

# revision identifiers, used by Alembic.
revision = 'edea8eca3ae8'
down_revision = 'ec9c4deb0227'
branch_labels = None
depends_on = None


def upgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.alter_column('user', 'birthdate',
               existing_type=mysql.DATETIME(),
               nullable=False)
    # ### end Alembic commands ###


def downgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.alter_column('user', 'birthdate',
               existing_type=mysql.DATETIME(),
               nullable=True)
    # ### end Alembic commands ###
