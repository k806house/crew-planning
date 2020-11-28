import os
from flask import Flask

from core.db import create_engine
from core.handlers.core import construct_blueprint


def create_app():
    app_config = os.getenv('APP_SETTINGS', 'core.config.DevConfig')
    app = Flask(__name__)
    app.config.from_object(app_config)
    app.db = create_engine(app.config['DB_URL'], app.config['DB_ENV'])
    app.register_blueprint(construct_blueprint(), url_prefix='/v1')
    return app