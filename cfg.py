import os

print('Read cfg.py')
DEBUG = os.environ.get('CUSG_DEBUG', 'NO') == 'YES'
TESTING = os.environ.get('CUSG_TESTING', 'NO') == 'YES'
LOCAL_SECRET = 'top-secret-local-debug'
SECRET = LOCAL_SECRET if DEBUG else os.environ.get('CUSG_SECRET', None)
if not SECRET: raise EnvironmentError('CUSG_SECRET not set!')
DB_CONNETION_STRING = 'sqlite:///app.db'
if TESTING: DB_CONNETION_STRING = 'sqlite:///app_test.db'
print('DEBUG', DEBUG)
print('TESTING', TESTING)
print('CONNECTION STRING', DB_CONNETION_STRING)
