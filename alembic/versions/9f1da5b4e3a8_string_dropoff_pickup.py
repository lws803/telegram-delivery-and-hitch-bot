"""String for dropoff pickup

Revision ID: 9f1da5b4e3a8
Revises: 0818d7a4c7ed
Create Date: 2020-05-01 01:24:05.699945

"""
from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import mysql

# revision identifiers, used by Alembic.
revision = '9f1da5b4e3a8'
down_revision = '0818d7a4c7ed'
branch_labels = None
depends_on = None


def upgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.add_column('requests', sa.Column('location_dropoff', sa.String(length=250), nullable=True))
    op.add_column('requests', sa.Column('location_pickup', sa.String(length=250), nullable=True))
    op.drop_column('requests', 'location')
    # ### end Alembic commands ###


def downgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.add_column('requests', sa.Column('location', mysql.JSON(), nullable=True))
    op.drop_column('requests', 'location_pickup')
    op.drop_column('requests', 'location_dropoff')
    # ### end Alembic commands ###
