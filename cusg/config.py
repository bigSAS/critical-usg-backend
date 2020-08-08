import os
from os import environ

DEBUG = environ.get('CUSG_DEBUG', 'NO') == 'YES'
ENV = environ.get('CUSG_ENV', 'prod') # when testing set CUSG_ENV=test


class Config:
    SECRET_KEY = os.environ['CUSG_SECRET']
    FLASK_APP = 'wsgi:cusg'
    FLASK_DEBUG = DEBUG

    # Database
    SQLALCHEMY_DATABASE_URI = f"postgresql://postgres:postgres@db:5432/cusg_db_{ENV}"
    SQLALCHEMY_ECHO = False
    SQLALCHEMY_TRACK_MODIFICATIONS = False


class TConfig:
    SECRET_KEY = "secret"
    FLASK_APP = 'wsgi:cusg'
    FLASK_DEBUG = True

    # Database
    SQLALCHEMY_DATABASE_URI = f"postgresql://postgres:postgres@localhost:5432/cusg_db_test"
    SQLALCHEMY_ECHO = False
    SQLALCHEMY_TRACK_MODIFICATIONS = False
