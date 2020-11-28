import os


class DevConfig:
    DEBUG = True
    UPLOAD_FOLDER = '/mnt/core/schedules'
    DB_HOST = os.getenv('DB_HOST')
    DB_PORT = os.getenv('DB_PORT')
    DB_NAME = os.getenv('DB_NAME')
    DB_USER = os.getenv('DB_USER')
    DB_PASSWORD = os.getenv('DB_PASSWORD')
    DB_ENV = os.getenv('DB_ENV')
    DB_URL = "postgresql+psycopg2://{0}:{1}@{2}:{3}/{4}".format(
        DB_USER,
        DB_PASSWORD,
        DB_HOST,
        DB_PORT,
        DB_NAME,
    )
