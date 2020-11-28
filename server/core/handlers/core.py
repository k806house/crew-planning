import os
import json
from datetime import datetime

from flask import Blueprint, Response, request, redirect, current_app, flash, url_for, jsonify
from flask_cors import CORS
from sqlalchemy import func, select, and_
from werkzeug.utils import secure_filename
from werkzeug.exceptions import BadRequest

from core.db.models import depot_table, train_table, schedule_train_table
from core.crew_pairing import compute_crew_pairings
from core.cp2workers import cp2workers
from core.utils import allowed_file, format_pairings, format_schedule


def construct_blueprint():
    core_bp = Blueprint('core', __name__)
    CORS(core_bp)

    @core_bp.route('/upload_schedule', methods=['GET', 'POST'])
    def crew_pairing():
        if request.method == 'POST':
            # check if the post request has the file part
            if 'file' not in request.files:
                flash('No file part')
                return redirect(request.url)
            file = request.files['file']
            # if user does not select file, browser also
            # submit an empty part without filename
            if file.filename == '':
                flash('No selected file')
                return redirect(request.url)
            if file and allowed_file(file.filename):
                filename = secure_filename(file.filename)
                save_path = os.path.join(current_app.config['UPLOAD_FOLDER'],
                                         filename)
                file.save(save_path)
                pairings = compute_crew_pairings(save_path)
                schedule1, schedule2 = cp2workers(pairings)
                return jsonify({
                    'Самарское депо': format_schedule(schedule1),
                    'Пензенское депо': format_schedule(schedule2)
                })
                # return redirect(url_for('crew_pairing', filename=filename))
        return '''
        <!doctype html>
        <title>Generate crew pairings</title>
        <h1>Upload schedule</h1>
        <form method=post enctype=multipart/form-data>
        <input type=file name=file>
        <input type=submit value=Upload>
        </form>
        '''

    @core_bp.route('/route', methods=['POST', 'DELETE'])
    def route():
        if request.method == 'POST':
            data = request.get_json(force=True)
            if not valid_route_post(data):
                raise BadRequest('Data doesn\'t contain all required fields')

            route_post(data)

            return Response(
                json.dumps({'status': 'ok'}),
                status=204, mimetype='application/json'
            )

        elif request.method == 'DELETE':
            data = request.get_json(force=True)
            if not valid_route_delete(data):
                raise BadRequest('Data doesn\'t contain all required fields')

            route_delete(data)

            return Response(
                json.dumps({'status': 'ok'}),
                status=204, mimetype='application/json'
            )

    return core_bp


def valid_route_post(data):
    required = [
        'trainTitle',
        'from',
        'to',
        'startDate',
        'endDate'
    ]

    for field in required:
        if field not in data:
            return False

    return True


def valid_route_delete(data):
    required = [
        'trainTitle',
        'from',
        'startDate'
    ]

    for field in required:
        if field not in data:
            return False

    return True


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
