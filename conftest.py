import os
import re

import pytest
import sqlalchemy
import sqlalchemy.future
import sqlmodel
import sqlmodel.pool

import dot_init  # noqa: F401
import models

# set app env
os.environ["APP_ENV"] = "tst"

test_db_name = os.environ.get("DATABASE_TEST_URL")
connect_args: dict = {}

assert test_db_name

if "sqlite" in test_db_name:
    # sqlite specific
    connect_args = {"check_same_thread": False}

engine = sqlmodel.create_engine(
    test_db_name,
    connect_args=connect_args,
    poolclass=sqlmodel.pool.StaticPool,
)


def database_tables_create(engine: sqlalchemy.future.Engine):
    sqlmodel.SQLModel.metadata.create_all(engine)


def database_tables_drop(engine: sqlalchemy.future.Engine):
    sqlmodel.SQLModel.metadata.drop_all(engine)


def database_tables_init(engine: sqlalchemy.future.Engine):
    # initialize hypertables
    _session = sqlmodel.Session(engine)

    # note: requires timescaledb support
    # session.execute("select create_hypertable('events', 'timestamp')")


# Set up the database once
database_tables_drop(engine)
database_tables_create(engine)
database_tables_init(engine)


@pytest.fixture(name="db_session")
def session_fixture():
    connection = engine.connect()
    transaction = connection.begin()

    # begin a nested transaction (using SAVEPOINT)
    nested = connection.begin_nested()

    session = sqlmodel.Session(engine)

    # if the application code calls session.commit, it will end the nested transaction
    # when that happens, start a new one.
    @sqlalchemy.event.listens_for(session, "after_transaction_end")
    def end_savepoint(session, transaction):
        nonlocal nested
        if not nested.is_active:
            nested = connection.begin_nested()

    # yield session to test
    yield session

    session.close()
    # rollback the overall transaction, restoring the state before the test ran
    transaction.rollback()
    connection.close()
