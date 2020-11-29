import os
import json
from datetime import datetime

import pandas as pd
from flask import Blueprint, Response, request, redirect, current_app, flash, url_for, jsonify
from flask_cors import CORS
from sqlalchemy import func, select, and_
from werkzeug.utils import secure_filename
from werkzeug.exceptions import BadRequest

from core.db.models import depot_table, train_table, schedule_train_table
from core.crew_pairing import compute_crew_pairings
from core.cp2workers import cp2workers
from core.utils import allowed_file, format_pairings, format_schedule


REQUIRED_FIELDS_ROUTE_POST = [
    'trainTitle',
    'from',
    'to',
    'startDate',
    'endDate'
]

REQUIRED_FIELDS_ROUTE_DELETE = [
    'trainTitle',
    'from',
    'startDate'
]

REQUIRED_FIELDS_TRAIN_DELETE = [
    'trainTitle'
]

REQUIRED_FIELDS_CREW_SCHEDULE_POST = [
    'startDate',
    'endDate'
]


def construct_blueprint():
    core_bp = Blueprint('core', __name__)
    CORS(core_bp)

    @core_bp.route('/crew_schedule', methods=['GET'])
    def crew_pairing():
        if request.method == 'GET':
            data = request.get_json(force=True)
            if not valid_simple(data, REQUIRED_FIELDS_CREW_SCHEDULE_POST):
                raise BadRequest('Data doesn\'t contain all required fields')
            start_date = data['startDate']
            end_date = data['endDate']
            schedule_train_df = get_schedule_train_df(start_date, end_date)


            # ДАВИД В schedule_train_df ЛЕЖИТ ТАБЛИЦА schedule_train
            # ИЗ БАЗЫ, СДЕЛАЙ ТАК ЧТОБЫ АЛГОРИТМ ЗАРАБОТАЛ С ЭТОЙ ХЕРНЕЙ
            pairings = compute_crew_pairings(schedule_train_df)
            schedule1, schedule2 = cp2workers(pairings)
            return jsonify({
                'Самарское депо': format_schedule(schedule1),
                'Пензенское депо': format_schedule(schedule2)
            })


    @core_bp.route('/route', methods=['POST', 'DELETE'])
    def route():
        if request.method == 'POST':
            data = request.get_json(force=True)
            if not valid_simple(data, REQUIRED_FIELDS_ROUTE_POST):
                raise BadRequest('Data doesn\'t contain all required fields')

            route_post(data)

            return Response(
                json.dumps({'status': 'ok'}),
                status=204, mimetype='application/json'
            )

        elif request.method == 'DELETE':
            data = request.get_json(force=True)
            if not valid_simple(data, REQUIRED_FIELDS_ROUTE_DELETE):
                raise BadRequest('Data doesn\'t contain all required fields')

            route_delete(data)

            return Response(
                json.dumps({'status': 'ok'}),
                status=204, mimetype='application/json'
            )

    @core_bp.route('/train', methods=['DELETE'])
    def train():
        if request.method == 'DELETE':
            data = request.get_json(force=True)
            if not valid_simple(data, REQUIRED_FIELDS_TRAIN_DELETE):
                raise BadRequest('Data doesn\'t contain all required fields')

            train_delete(data)

            return Response(
                json.dumps({'status': 'ok'}),
                status=204, mimetype='application/json'
            )

    # @core_bp.route('/crew', methods=['GET'])
    # def crew():



    return core_bp


def valid_simple(data, required):
    for field in required:
        if field not in data:
            return False

    return True


def get_schedule_train_df(date_start, date_end):
    date_start = date_to_ts(date_start)
    date_end = date_to_ts(date_end)
    schedule_train_df = pd.read_sql(
        '''
            select * from schedule_train
            where schedule_train.date_start >= '{0}' and schedule_train.date_end <= '{1}';
        '''.format(date_start, date_end),
        con=current_app.db
    )
    return schedule_train_df


def date_to_ts(date):
    date, time_ = date.split()
    dd, mm, yy = date.split('/')
    return f'{yy}-{mm}-{dd} {time_}'


def route_post(data):
    with current_app.db.connect() as conn:
        with conn.begin():
            title = data['trainTitle']
            fr = data['from']
            to = data['to']

            train = get_train_record(conn, title)
            if train is None:
                train_id = insert_train(conn, data)
            else:
                train_id = train['id']

            departure = get_depot_record(conn, fr)
            if departure is None:
                departure_id = insert_depot(conn, data, 'from')
            else:
                departure_id = departure['id']

            arrival = get_depot_record(conn, to)
            if arrival is None:
                arrival_id = insert_depot(conn, data, 'to')
            else:
                arrival_id = arrival['id']

            query = {
                'id': max_id_schedule_train(conn),
                'train_id': train_id,
                'departure_id': departure_id,
                'arrival_id': arrival_id,
                'date_start': format_date(data['startDate']),
                'date_end': format_date(data['endDate'])
            }

            conn.execute(schedule_train_table.insert(), [query])


def route_delete(data):
    with current_app.db.connect() as conn:
        with conn.begin():
            title = data['trainTitle']
            fr = data['from']
            date_start = format_date(data['startDate']).date()

            train = get_train_record(conn, title)
            if train is None:
                raise BadRequest(f'Train with title \'{title}\' not in database')
            train_id = train['id']

            departure = get_depot_record(conn, fr)
            if departure is None:
                raise BadRequest(f'Depot with name \'{fr}\' not in database')
            departure_id = departure['id']

            del_sch_tr_q = schedule_train_table.delete().where(
                and_(
                    schedule_train_table.c.train_id == train_id,
                    schedule_train_table.c.departure_id == departure_id,
                    func.date(schedule_train_table.c.date_start) == date_start
                )
            )

            conn.execute(del_sch_tr_q)


def train_delete(data):
    with current_app.db.connect() as conn:
        with conn.begin():
            title = data['trainTitle']
            train = get_train_record(conn, title)
            if train is None:
                raise BadRequest(f'Train with title \'{title}\' not in database')
            train_id = train['id']

            del_sch_tr_q = schedule_train_table.delete().where(
                and_(
                    schedule_train_table.c.train_id == train_id,
                )
            )

            conn.execute(del_sch_tr_q)


def format_date(date):
    return datetime.strptime(date, '%d/%m/%Y %H:%M:%S')


def get_train_record(conn, title):
    train_record_q = train_table.select().where(
        train_table.c.title == title
    )
    rows = conn.execute(train_record_q)
    return rows.fetchone()


def get_depot_record(conn, depot):
    depot_record_q = depot_table.select().where(
        depot_table.c.name == depot
    )
    rows = conn.execute(depot_record_q)
    return rows.fetchone()


def insert_train(conn, data):
    query = {
        'id': max_id_train(conn),
        'title': data['trainTitle'],
        'type': 'passenger'
    }

    train_id = conn.execute(
                train_table.insert(),
                query
            ).inserted_primary_key[0]

    return train_id


def insert_depot(conn, data, field):
    query = {
        'id': max_id_depot(conn),
        'name': data[field]
    }

    depot_id = conn.execute(
                depot_table.insert(),
                query
            ).inserted_primary_key[0]

    return depot_id


def max_id_schedule_train(conn):
    schedule_train_q = select(
        [func.max(schedule_train_table.c.id)]
    )

    max_id = conn.execute(schedule_train_q).scalar()
    return max_id + 1


def max_id_train(conn):
    train_q = select(
        [func.max(train_table.c.id)]
    )

    max_id = conn.execute(train_q).scalar()
    return max_id + 1


def max_id_depot(conn):
    depot_q = select(
        [func.max(depot_table.c.id)]
    )

    max_id = conn.execute(depot_q).scalar()
    return max_id + 1
