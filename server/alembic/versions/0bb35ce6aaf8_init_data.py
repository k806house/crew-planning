"""Init data

Revision ID: 0bb35ce6aaf8
Revises: 569935bd69a9
Create Date: 2020-11-28 14:27:04.062866

"""
from alembic import op
from datetime import datetime
from sqlalchemy.sql import table, column
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = '0bb35ce6aaf8'
down_revision = '569935bd69a9'
branch_labels = None
depends_on = None

DATA_PATH = '/mnt/data/rzd.csv'

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


train_type = sa.Enum('passenger', 'freight', name='train_type')

train_table = table(
    'train',
    column('id', sa.Integer),
    column('title', sa.String),
    column('type', train_type),
    column('route_id', sa.Integer),
)

depot_table = table(
    'depot',
    column('id', sa.Integer),
    column('name', sa.String),
)

route_table = table(
    'route',
    column('id', sa.Integer),
    column('departure_id', sa.Integer),
    column('arrival_id', sa.Integer),
)

crew_table = table(
    'crew',
    column('id', sa.Integer),
    column('head', sa.String),
    column('base_station_id', sa.Integer),
)

schedule_table = table(
    'schedule',
    column('id', sa.Integer),
    column('train_id', sa.Integer),
    column('crew_id', sa.Integer),
    column('date_start', sa.Date),
    column('date_end', sa.Date),
)


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
                'crew_id': 0,
                'date_start': datetime.fromisoformat(departure),
                'date_end': datetime.fromisoformat(arrival),
            }
            res.append(tmp)

    return res

def upgrade():
    op.bulk_insert(
        depot_table,
        [
            {'id': 1, 'name': 'Самара'},
            {'id': 2, 'name': 'Пенза-1'}
        ]
    )

    op.bulk_insert(
        route_table,
        [
            {'id': 1, 'departure_id': 1, 'arrival_id': 2}, # Самара - Пенза
            {'id': 2, 'departure_id': 2, 'arrival_id': 1}  # Пенза - Самара
        ]
    )

    op.bulk_insert(
        train_table,
        [
            {'id': 1, 'title': '133H', 'type': 'passenger', 'route_id': 1},
            {'id': 2, 'title': '131У', 'type': 'passenger', 'route_id': 1},
            {'id': 3, 'title': '101Й', 'type': 'passenger', 'route_id': 1},
            {'id': 4, 'title': '132У', 'type': 'passenger', 'route_id': 2},
            {'id': 5, 'title': '124В', 'type': 'passenger', 'route_id': 2},
            {'id': 6, 'title': '102Й', 'type': 'passenger', 'route_id': 2},
            {'id': 7, 'title': '123Н', 'type': 'passenger', 'route_id': 1},
            {'id': 8, 'title': '133С', 'type': 'passenger', 'route_id': 2},
            {'id': 9, 'title': '117Й', 'type': 'passenger', 'route_id': 1},
            {'id': 10, 'title': '107Й', 'type': 'passenger', 'route_id': 1},
            {'id': 11, 'title': '109Й', 'type': 'passenger', 'route_id': 1},
            {'id': 12, 'title': '118С', 'type': 'passenger', 'route_id': 2},
            {'id': 13, 'title': '111С', 'type': 'passenger', 'route_id': 2},
            {'id': 14, 'title': '107Ж', 'type': 'passenger', 'route_id': 2},
            {'id': 15, 'title': '111У', 'type': 'passenger', 'route_id': 1},
            {'id': 16, 'title': '110Й', 'type': 'passenger', 'route_id': 2},
        ]
    )

    op.bulk_insert(
        schedule_table,
        get_data()
    )


def downgrade():
    pass
