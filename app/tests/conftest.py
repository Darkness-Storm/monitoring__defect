import os
from contextlib import redirect_stdout, suppress

import pytest

from playhouse.sqlite_ext import SqliteExtDatabase

from app.app import create_web_app
#import app
from app.models import create_table, db_wrapper, Component, Organisation, Status, ModelBus, Location, drop_table
import config


@pytest.fixture()
def app(database):
    app = create_web_app('config.TestingConfig')
    create_table(db_wrapper.database)
    create_test_data_problem(db_wrapper.database)

    # other setup can go here

    yield app

    # clean up / reset resources here
    # print(app.config['DATABASE']['name'])
    drop_table(db_wrapper.database)
    db_wrapper.database.close()
    with suppress(FileNotFoundError):
        os.remove(app.config['DATABASE']['name'])


def create_test_data_problem(db):
    with db:

        Component.get_or_create(number='component test number', descr='component test descr', id=1)
        Status.get_or_create(descr='status test descr', id=1)
        ModelBus.get_or_create(descr='model test descr1', id=1)
        ModelBus.get_or_create(descr='model test descr2', id=2)
        Location.get_or_create(descr='location test descr', id=1)
        Organisation.get_or_create(descr='org test descr', legal_form='org test form', legal_sity='org test sity', id=1)


@pytest.fixture()
def client(app):
    return app.test_client()


@pytest.fixture()
def runner(app):
    return app.test_cli_runner()


@pytest.fixture()
def database():
    return db_wrapper.database
    
# @pytest.fixture()
# def db_app(tmpdir):
#     path_db = os.path.join(tmpdir, "sqa_test.db")
#     print(path_db)
#     db = SqliteExtDatabase(path_db, pragmas=(('cache_size', -1024 * 64), ('journal_mode', 'wal')))
#     create_table(db)

#     yield db

#     with suppress(FileNotFoundError):
#         os.remove(path_db)