import os
from os import environ

ENV = environ.get('CUSG_ENV', 'prod')  # when testing set CUSG_ENV=test

HOUR = (60 * 60)
DAY = (HOUR * 24)

DB_URI = os.environ.get('CUSG_DB_CONNETION_STRING', f"postgresql://postgres:postgres@db:5432/cusg_db")
SECRET = os.environ.get('CUSG_SECRET', None)

if ENV == 'prod' and not SECRET: raise EnvironmentError('CUSG_SECRET not set!')
else: SECRET = 'local'


class Config:
    SECRET_KEY = SECRET
    JWT_ACCESS_TOKEN_EXPIRES = (1 * DAY)

    SQLALCHEMY_DATABASE_URI = DB_URI
    SQLALCHEMY_ECHO = False
    SQLALCHEMY_TRACK_MODIFICATIONS = False


class TConfig:
    SECRET_KEY = "secret"
    JWT_ACCESS_TOKEN_EXPIRES = False

    SQLALCHEMY_DATABASE_URI = "postgresql://postgres:postgres@localhost:5432/cusg_db_test"
    SQLALCHEMY_ECHO = False
    SQLALCHEMY_TRACK_MODIFICATIONS = False
