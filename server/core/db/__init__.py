import sqlalchemy as sa


def create_engine(db_url, db_env):
    if db_env == 'dev':
        engine = sa.create_engine(
            db_url
        )
    else:
        engine = sa.create_engine(
            db_url,
            connect_args={'sslmode':'verify-full'},
        )
    return engine
