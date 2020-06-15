from os import environ

DEBUG_LOCAL = False
# noinspection PyBroadException
try:
    from config_local import DEBUG as LOCAL_DEBUG
    DEBUG_LOCAL = LOCAL_DEBUG
    print('#' * 50)
    print('LOCAL DEBUG:', DEBUG_LOCAL)
    HAS_LOCAL_CONFIG = True
except:
    HAS_LOCAL_CONFIG = False

print('#' * 50)
print('Configuration')
print('#' * 50)
DEBUG = DEBUG_LOCAL if HAS_LOCAL_CONFIG else environ.get('CUSG_DEBUG', 'NO') == 'YES'

TESTING = environ.get('CUSG_TESTING', 'NO') == 'YES'
LOCAL_SECRET = 'top-secret-local-debug'
SECRET = LOCAL_SECRET if DEBUG else environ.get('CUSG_SECRET', None)
if not SECRET: raise EnvironmentError('CUSG_SECRET not set!')
DB_CONNETION_STRING = environ['CUSG_DB_CONNETION_STRING'] \
    if environ.get('CUSG_DB_CONNETION_STRING', None) else 'sqlite:///app.db'
if TESTING: DB_CONNETION_STRING = 'sqlite:///app_test.db'
print('DEBUG:', 'yes' if DEBUG else 'no')
print('TESTING:', 'yes' if TESTING else 'no')
print('DB CONNECTION STRING:', DB_CONNETION_STRING)
print('#' * 50)


class Config:
    SECRET_KEY = SECRET
    FLASK_APP = 'wsgi'
    FLASK_DEBUG = DEBUG

    # Database
    SQLALCHEMY_DATABASE_URI = DB_CONNETION_STRING
    SQLALCHEMY_ECHO = False
    SQLALCHEMY_TRACK_MODIFICATIONS = False
