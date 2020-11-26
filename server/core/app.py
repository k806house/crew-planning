import os
from flask import Flask

from core.handlers.core import construct_blueprint


def create_app():
    app_config = os.getenv('APP_SETTINGS', 'core.config.DevConfig')
    app = Flask(__name__)
    app.config.from_object(app_config)
    app.register_blueprint(construct_blueprint())
    return app