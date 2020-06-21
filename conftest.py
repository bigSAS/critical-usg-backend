import pytest
from webtest import TestApp as TApp

from wsgi import app as application
from db.model import db as database, User

USER = {
    'email': 'jimmy@choo.io',
    'plaintext_password': 'jimmyh',
    'is_superuser': False
}

ADMIN = {
    'email': 'sas@kodzi.io',
    'plaintext_password': 'sas',
    'is_superuser': True
}


@pytest.fixture(scope='session')
def db():
    return database


@pytest.fixture(scope='session')
def dbsession(db):
    yield db.session


@pytest.fixture(scope='session')
def app(db):
    apk = application
    db.init_app(apk)
    db.init_app(apk)
    with apk.app_context():
        user = User(**USER)
        admin = User(**ADMIN)
        db.session.add(user)
        db.session.add(admin)
        db.session.commit()
        return apk


@pytest.fixture(scope='session')
def client(app) -> TApp:
    return TApp(app)


@pytest.fixture(scope='function')
def get_headers(client):
    def get_headers_with_auth(role: str = 'user'):
        if role == 'user':
            email = USER['email']
            password = USER['plaintext_password']
        elif role == 'admin':
            email = ADMIN['email']
            password = ADMIN['plaintext_password']
        else: raise ValueError(f'invalid role: {role}')
        response = client.post_json(
            '/api/token-auth',
            {
                'email': email,
                'password': password
            }
        )
        jwt = response.json['data']['token']
        headers = {
            'Content-type': 'application/json',
            'Authorization': f'Bearer {jwt}'
        }
        return headers
    return get_headers_with_auth
