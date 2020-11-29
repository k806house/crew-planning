from enum import Enum

import sqlalchemy as sa
from sqlalchemy import MetaData, Column, DateTime, text
from sqlalchemy.ext.declarative import as_declarative, declared_attr


# @see https://alembic.sqlalchemy.org/en/latest/naming.html
convention = {
    'all_column_names': lambda constraint, table: '_'.join([
        column.name for column in constraint.columns.values()
    ]),
    'ix': 'ix__%(all_column_names)s',
    'uq': 'uq__%(table_name)s__%(all_column_names)s',
    'ck': 'ck__%(table_name)s__%(constraint_name)s',
    'fk': 'fk__%(table_name)s__%(all_column_names)s__%(referred_table_name)s',
    'pk': 'pk__%(table_name)s'
}

metadata = MetaData(naming_convention=convention)


@as_declarative(metadata=metadata)
class Base:
    """Base class for all models"""
    pass

class TrainType(Enum):
    passenger = 'passenger'
    freight = 'freight'


class Train(Base):
    __tablename__ = 'train'

    id = sa.Column(sa.Integer, primary_key=True)
    title = sa.Column(sa.String(256), nullable=False)
    type = sa.Column(sa.Enum(TrainType), nullable=False)


train_table = Train.__table__


class Depot(Base):
    __tablename__ = 'depot'

    id = sa.Column(sa.Integer, primary_key=True)
    name = sa.Column(sa.String(256), nullable=False)


depot_table = Depot.__table__


class Crew(Base):
    __tablename__ = 'crew'

    id = sa.Column(sa.Integer, primary_key=True)
    head = sa.Column(sa.String(256), nullable=False)
    base_station_id = sa.Column(sa.Integer, nullable=False)


crew_table = Crew.__table__


class ScheduleTrain(Base):
    __tablename__ = 'schedule_train'

    id = sa.Column(sa.Integer, primary_key=True)
    train_id = sa.Column(sa.Integer, nullable=False)
    departure_id = sa.Column(sa.Integer, nullable=False)
    arrival_id = sa.Column(sa.Integer, nullable=False)
    date_start = sa.Column(sa.DateTime, nullable=False)
    date_end = sa.Column(sa.DateTime, nullable=False)


schedule_train_table = ScheduleTrain.__table__


class ScheduleCrew(Base):
    __tablename__ = 'schedule_crew'

    id = sa.Column(sa.Integer, primary_key=True)
    schedule_train_id_1 = sa.Column(sa.Integer, nullable=False)
    schedule_train_id_2 = sa.Column(sa.Integer, nullable=False)
    crew_id = sa.Column(sa.Integer, nullable=False)


schedule_crew_table = ScheduleCrew.__table__
