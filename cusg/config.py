import os
from os import environ

DEBUG = environ.get('CUSG_DEBUG', 'NO') == 'YES'
ENV = environ.get('CUSG_ENV', 'prod')  # when testing set CUSG_ENV=test

HOUR = (60 * 60)
DAY = (HOUR * 24)

DB_URI = os.environ.get('CUSG_DB_CONNETION_STRING', f"postgresql://postgres:postgres@db:5432/cusg_db_{ENV}")


class Config:
    SECRET_KEY = os.environ['CUSG_SECRET']
    JWT_ACCESS_TOKEN_EXPIRES = (1 * HOUR) if not DEBUG else (360 * DAY)
    FLASK_APP = 'wsgi:cusg'
    FLASK_DEBUG = DEBUG
    FLASK_ENVIRONMENT = 'development' if DEBUG else 'production'

    # Database
    SQLALCHEMY_DATABASE_URI = DB_URI
    SQLALCHEMY_ECHO = False
    SQLALCHEMY_TRACK_MODIFICATIONS = False


class TConfig:
    SECRET_KEY = "secret"
    JWT_ACCESS_TOKEN_EXPIRES = False
    FLASK_APP = 'wsgi:cusg'
    FLASK_DEBUG = True
    FLASK_ENVIRONMENT = 'development' if DEBUG else 'production'

    # Database
    SQLALCHEMY_DATABASE_URI = "postgresql://postgres:postgres@localhost:5432/cusg_db_test"
    SQLALCHEMY_ECHO = False
    SQLALCHEMY_TRACK_MODIFICATIONS = False
