import os
from os import environ

DB_CONNETION_STRING = os.environ['CUSG_DB_CONNETION_STRING']
print('DB_CONNETION_STRING', DB_CONNETION_STRING)
DEBUG = environ.get('CUSG_DEBUG', 'NO') == 'YES'
print('DEBUG', DEBUG)


class Config:
    SECRET_KEY = os.environ['CUSG_SECRET']
    FLASK_APP = 'wsgi'
    FLASK_DEBUG = DEBUG

    # Database
    SQLALCHEMY_DATABASE_URI = DB_CONNETION_STRING
    SQLALCHEMY_ECHO = False
    SQLALCHEMY_TRACK_MODIFICATIONS = False
