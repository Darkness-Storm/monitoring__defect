import os


db_path = '\\\\gaz.ru\\paz\\SQA\\Database\\'
#db_path = 'd:\\Projects\\'
db_name = 'sqa.db'
con_str = os.path.join(db_path, db_name)
TMPDIR = 'tmp'

class Config(object):
    DEBUG = False
    CSRF_ENABLED = True
    WTF_CSRF_SECRET_KEY = 'dsofpkoasodksap'
    SECRET_KEY = 'dFcIh3Ckt5TyKNJRfi9u'
    DATABASE = {
        'name': con_str,
        'engine': 'playhouse.sqlite_ext.SqliteExtDatabase',
        'pragmas': {'cache_size': -1024 * 64, 'journal_mode': 'wal'}
    }


class ProductionConfig(Config):
    DEBUG = False


class DevelopConfig(Config):
    DEBUG = True


class TestingConfig(Config):
    DEBUG = True
    TESTING = True
    CSRF_ENABLED = False
    WTF_CSRF_ENABLED = False
    WTF_CSRF_SECRET_KEY = ''
    DATABASE = {
        'name': 'sqa_test.db',
        'engine': 'playhouse.sqlite_ext.SqliteExtDatabase',
        'pragmas': {'cache_size': -1024 * 64, 'journal_mode': 'wal'}
    }
