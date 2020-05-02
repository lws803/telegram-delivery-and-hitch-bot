"""combined tables

Revision ID: a7e59309f33b
Revises: 9881e71bc7bc
Create Date: 2020-04-30 15:27:52.100374

"""
from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import mysql

# revision identifiers, used by Alembic.
revision = 'a7e59309f33b'
down_revision = '9881e71bc7bc'
branch_labels = None
depends_on = None


def upgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.create_table('requests',
    sa.Column('id', sa.BigInteger(), nullable=False),
    sa.Column('role', sa.Enum('DRIVER', 'CUSTOMER', name='roletype'), nullable=False),
    sa.Column('chat_id', sa.BigInteger(), nullable=False),
    sa.Column('location', mysql.JSON(), nullable=True),
    sa.Column('time', sa.DateTime(), nullable=True),
    sa.Column('price', sa.Float(), nullable=True),
    sa.Column('package_type', sa.String(length=250), nullable=True),
    sa.Column('state', sa.Enum('ACTIVE', 'DONE', name='statetype'), nullable=False),
    sa.Column('additional_info', sa.String(length=250), nullable=True),
    sa.PrimaryKeyConstraint('id')
    )
    op.drop_table('customer_requests')
    op.drop_table('driver_requests')
    # ### end Alembic commands ###


def downgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.create_table('driver_requests',
    sa.Column('id', mysql.BIGINT(), autoincrement=True, nullable=False),
    sa.Column('chat_id', mysql.BIGINT(), autoincrement=False, nullable=False),
    sa.Column('additional_info', mysql.VARCHAR(collation='utf8mb4_bin', length=250), nullable=True),
    sa.Column('location', mysql.JSON(), nullable=True),
    sa.Column('state', mysql.ENUM('ACTIVE', 'DONE', collation='utf8mb4_bin'), nullable=False),
    sa.PrimaryKeyConstraint('id'),
    mysql_collate='utf8mb4_bin',
    mysql_default_charset='utf8mb4',
    mysql_engine='InnoDB'
    )
    op.create_table('customer_requests',
    sa.Column('id', mysql.BIGINT(), autoincrement=True, nullable=False),
    sa.Column('chat_id', mysql.BIGINT(), autoincrement=False, nullable=False),
    sa.Column('additional_info', mysql.VARCHAR(collation='utf8mb4_bin', length=250), nullable=True),
    sa.Column('location', mysql.JSON(), nullable=True),
    sa.Column('time', mysql.DATETIME(), nullable=False),
    sa.Column('price', mysql.FLOAT(), nullable=False),
    sa.Column('package_type', mysql.VARCHAR(collation='utf8mb4_bin', length=250), nullable=False),
    sa.Column('state', mysql.ENUM('ACTIVE', 'DONE', collation='utf8mb4_bin'), nullable=False),
    sa.PrimaryKeyConstraint('id'),
    mysql_collate='utf8mb4_bin',
    mysql_default_charset='utf8mb4',
    mysql_engine='InnoDB'
    )
    op.drop_table('requests')
    # ### end Alembic commands ###
