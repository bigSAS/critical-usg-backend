import os

DEBUG = os.environ.get('CUSG_DEBUG', 'NO') == 'YES'
LOCAL_SECRET = 'top-secret-local-debug'
SECRET = LOCAL_SECRET if DEBUG else os.environ.get('CUSG_SECRET', None)
if not SECRET: raise EnvironmentError('CUSG_SECRET not set!')
