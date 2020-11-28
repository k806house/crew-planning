"""init db

Revision ID: 569935bd69a9
Revises: 
Create Date: 2020-11-28 02:45:02.658873

"""
from datetime import datetime

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = '569935bd69a9'
down_revision = None
branch_labels = None
depends_on = None

DATA_PATH = '/mnt/data/rzd.csv'

train_type = sa.Enum('passenger', 'freight', name='train_type')

trains = {
    '133Н': 1,
    '131У': 2,
    '101Й': 3,
    '132У': 4,
    '124В': 5,
    '102Й': 6,
    '123Н': 7,
    '133С': 8,
    '117Й': 9,
    '107Й': 10,
    '109Й': 11,
    '118С': 12,
    '111С': 13,
    '107Ж': 14,
    '111У': 15,
    '110Й': 16
}

dep = {
    'Самара': 1,
    'Пенза-1': 2,
}


def get_data():
    res = []
    with open(DATA_PATH, 'r') as f:
        for i, record in enumerate(f):
            if i == 0:
                continue

            train,departure,fr,arrival,to = record.split(',')

            if not train:
                continue

            to = to.rstrip('\n')
            if fr not in ['Самара', 'Пенза-1'] or to not in ['Самара', 'Пенза-1']:
                continue

            tmp = {
                'id': i,
                'train_id': trains[train],
                'departure_id': dep[fr],
                'arrival_id': dep[to],
                'date_start': datetime.fromisoformat(departure),
                'date_end': datetime.fromisoformat(arrival),
            }
            res.append(tmp)

    return res


def upgrade():
    train_table = op.create_table(
        'train',
        sa.Column('id', sa.Integer(), primary_key=True),
        sa.Column('title', sa.String(length=256), nullable=False),
        sa.Column('type', train_type, nullable=False),
    )

    depot_table = op.create_table(
        'depot',
        sa.Column('id', sa.Integer(), primary_key=True),
        sa.Column('name', sa.String(length=256), nullable=False),
    )

    schedule_train_table = op.create_table(
        'schedule_train',
        sa.Column('id', sa.Integer(), primary_key=True),
        sa.Column('train_id', sa.Integer(), nullable=False),
        sa.Column('departure_id', sa.Integer(), nullable=False),
        sa.Column('arrival_id', sa.Integer(), nullable=False),
        sa.Column('date_start', sa.Date(), nullable=False),
        sa.Column('date_end', sa.Date(), nullable=False),
    )

    op.create_table(
        'crew',
        sa.Column('id', sa.Integer(), primary_key=True),
        sa.Column('head', sa.String(length=256), nullable=False),
        sa.Column('base_station_id', sa.Integer(), nullable=False),
    )

    op.create_table(
        'schedule_crew',
        sa.Column('id', sa.Integer(), primary_key=True),
        sa.Column('schedule_train_id', sa.Integer(), nullable=False),
        sa.Column('crew_id', sa.Integer(), nullable=False),
        sa.PrimaryKeyConstraint('id', name=op.f('pk__schedule_crew')),
    )

    op.bulk_insert(
        depot_table,
        [
            {'id': 1, 'name': 'Самара'},
            {'id': 2, 'name': 'Пенза-1'}
        ]
    )

    op.bulk_insert(
        train_table,
        [
            {'id': 1, 'title': '133H', 'type': 'passenger'},
            {'id': 2, 'title': '131У', 'type': 'passenger'},
            {'id': 3, 'title': '101Й', 'type': 'passenger'},
            {'id': 4, 'title': '132У', 'type': 'passenger'},
            {'id': 5, 'title': '124В', 'type': 'passenger'},
            {'id': 6, 'title': '102Й', 'type': 'passenger'},
            {'id': 7, 'title': '123Н', 'type': 'passenger'},
            {'id': 8, 'title': '133С', 'type': 'passenger'},
            {'id': 9, 'title': '117Й', 'type': 'passenger'},
            {'id': 10, 'title': '107Й', 'type': 'passenger'},
            {'id': 11, 'title': '109Й', 'type': 'passenger'},
            {'id': 12, 'title': '118С', 'type': 'passenger'},
            {'id': 13, 'title': '111С', 'type': 'passenger'},
            {'id': 14, 'title': '107Ж', 'type': 'passenger'},
            {'id': 15, 'title': '111У', 'type': 'passenger'},
            {'id': 16, 'title': '110Й', 'type': 'passenger'},
        ]
    )

    op.bulk_insert(
        schedule_train_table,
        get_data()
    )


def downgrade():
    op.drop_table('train')
    op.drop_table('depot')
    op.drop_table('schedule_train')
    op.drop_table('crew')
    op.drop_table('schedule_crew')
    train_type.drop(op.get_bind())