import os
from os import environ

DEBUG = environ.get('CUSG_DEBUG', 'NO') == 'YES'
print('DEBUG', DEBUG)
ENV = environ.get('CUSG_ENV', 'prod')


class Config:
    SECRET_KEY = os.environ['CUSG_SECRET']
    FLASK_APP = 'wsgi'
    FLASK_DEBUG = DEBUG

    # Database
    SQLALCHEMY_DATABASE_URI = f"postgresql://postgres:postgres@db:5432/cusg_db_{ENV}"
    SQLALCHEMY_ECHO = False
    SQLALCHEMY_TRACK_MODIFICATIONS = False
