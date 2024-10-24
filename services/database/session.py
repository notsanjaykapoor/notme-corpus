import os

import sqlalchemy
import sqlmodel

import dot_init  # noqa: F401

database_url = os.environ.get("DATABASE_URL")

assert database_url

connect_args: dict = {}

if "sqlite" in database_url:
    # sqlite specific args
    connect_args = {
        "check_same_thread": False,
    }

engine = sqlmodel.create_engine(database_url, echo=False, connect_args=connect_args)


# create and migrate db tables
def migrate():
    _migrate_sqlmodel()


def _migrate_sqlmodel():
    """migrate sqlmodel models"""
    sqlmodel.SQLModel.metadata.create_all(engine)


# get session object
def get() -> sqlmodel.Session:
    return sqlmodel.Session(engine)


@sqlalchemy.event.listens_for(engine, "connect")
def set_sqlite_pragma(dbapi_connection, connection_record):
    if "sqlite" in os.environ.get("DATABASE_URL"):
        # print("sqlachemy connect event")
        cursor = dbapi_connection.cursor()
        cursor.execute("pragma journal_mode=wal")
        cursor.close()


def table_names() -> list[str]:
    return sqlalchemy.inspect(engine).get_table_names()
