"""init db

Revision ID: 569935bd69a9
Revises: 
Create Date: 2020-11-28 02:45:02.658873

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = '569935bd69a9'
down_revision = None
branch_labels = None
depends_on = None

train_type = sa.Enum('passenger', 'freight', name='train_type')


def upgrade():
    op.create_table(
        'train',
        sa.Column('id', sa.Integer, primary_key=True),
        sa.Column('title', sa.String(length=256), nullable=False),
        sa.Column('type', train_type, nullable=False),
    )

    op.create_table(
        'depot',
        sa.Column('id', sa.Integer, primary_key=True),
        sa.Column('name', sa.String(length=256), nullable=False)
    )

    op.create_table(
        'route',
        sa.Column('id', sa.Integer, primary_key=True),
        sa.Column('departure_id', sa.Integer(), nullable=False),
        sa.Column('arrival_id', sa.Integer(), nullable=False),
    )

    op.create_table(
        'crew',
        sa.Column('id', sa.Integer, primary_key=True),
        sa.Column('head', sa.String(length=256), nullable=False),
        sa.Column('base_station_id', sa.Integer(), nullable=False)
    )


def downgrade():
    op.drop_table('train')
    op.drop_table('depot')
    op.drop_table('route')
    op.drop_table('crew')
    train_type.drop(op.get_bind())