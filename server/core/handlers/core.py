import os

from flask import Blueprint, request, redirect, current_app, flash, url_for, jsonify
from flask_cors import CORS
from werkzeug.utils import secure_filename

from core.crew_pairing import compute_crew_pairings
from core.cp2workers import cp2workers
from core.utils import allowed_file, format_pairings, format_schedule


def construct_blueprint():
    core_bp = Blueprint('core', __name__)
    CORS(core_bp)

    @core_bp.route('/', methods=['GET', 'POST'])
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

    return core_bp