from typing import Callable, Dict

import pytest
from webtest import TestApp as TApp

from cusg.repository.base import ObjectNotFoundError
from cusg.repository.repos import UserRepository, GroupUserRepository, UserGroupRepository
from cusg import create_app
from cusg.config import TConfig
from cusg.db.schema import db as database, User, GroupUser, UserGroup


USER = {
    'email': 'jimmy@choo.io',
    'plaintext_password': '12341234',
    'is_superuser': False
}

ADMIN = {
    'email': 'admin@choo.io',
    'plaintext_password': '12341234',
    'is_superuser': False
}

SUPERUSER = {
    'email': 'sas@kodzi.io',
    'plaintext_password': '12341234',
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
    apk = create_app(TConfig)
    db.init_app(apk)
    with apk.app_context():
        return apk


@pytest.fixture(scope='session')
def client(app) -> TApp:
    return TApp(app)


@pytest.fixture(scope='function')
def get_headers(client) -> Callable[[str], Dict[str, str]]:
    def get_headers_with_auth(role: str = 'user'):
        if role == 'nouser':
            return {'Content-type': 'application/json'}
        elif role == 'user':
            email = USER['email']
            password = USER['plaintext_password']
        elif role == 'admin':
            email = ADMIN['email']
            password = ADMIN['plaintext_password']
        elif role == 'superuser':
            email = SUPERUSER['email']
            password = SUPERUSER['plaintext_password']
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


@pytest.fixture(scope='function')
def get_user(app, dbsession):
    def getter(user_type='user'):
        def get_email():
            if user_type == 'user':
                return USER['email']
            elif user_type == 'admin':
                return ADMIN['email']
            elif user_type == 'superuser':
                return SUPERUSER['email']
            else:
                raise ValueError(f'invalid user type: {user_type}')

        def add_user(data, group=None):
            user = User(**data)
            UserRepository().save(user)
            if group is not None:
                g: UserGroup = UserGroupRepository().get_by(name=group)
                GroupUserRepository().save(GroupUser(group_id=g.id, user_id=user.id))

        with app.app_context():
            try:
                return UserRepository().get_by(email=get_email())
            except ObjectNotFoundError:
                if user_type == 'user': add_user(USER, 'USER')
                elif user_type == 'admin': add_user(ADMIN, 'ADMIN')
                elif user_type == 'superuser': add_user(SUPERUSER, None)
                return UserRepository().get_by(email=get_email())

    return getter


@pytest.fixture(scope='function')
def user(get_user) -> User:
    return get_user('user')


@pytest.fixture(scope='function')
def admin(get_user) -> User:
    return get_user('admin')


@pytest.fixture(scope='function')
def superuser(get_user) -> User:
    return get_user('superuser')
