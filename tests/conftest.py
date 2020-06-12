import pytest
from flask.testing import FlaskClient
from flask_migrate import Migrate

from app import app
from blueprints.auth import jwt
from db.model import db, bcrypt


@pytest.fixture
def client() -> FlaskClient:
    app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///app_test.db'
    db.init_app(app)
    bcrypt.init_app(app)
    jwt.init_app(app)
    migrate = Migrate(app, db)
    migrate.init_app(app)
    # app.config['TESTING'] = True

    with app.test_client() as test_client:
        yield test_client
