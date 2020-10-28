import uuid

import pytest
from webtest import TestApp as TApp

from cusg.db.schema import User
from cusg.repository.repos import UserRepository
from cusg.utils.http import ResponseStatus


def get_token_response(client: TApp, uid, email: str, password: str = '12341234', status: int = 200):
    return client.post_json(
        '/api/token-auth',
        {
            'uid': str(uid),
            'email': email,
            'password': password
        },
        status=status
    )


@pytest.mark.e2e
@pytest.mark.auth
def test_get_jwt(client: TApp, user, admin, superuser):
    """ test geting jwt token for admin and user """
    users = [user, admin, superuser]
    for usr in users:
        uid = uuid.uuid4()
        response = get_token_response(client, uid=uid, email=usr.email)
        print('response status code:', response.status_code)
        print('response json data:\n', response.json)
        assert response.json['uid'] == str(uid)
        assert response.json['status'] == ResponseStatus.OK.value
        assert response.json['data']['token'] is not None


@pytest.mark.e2e
@pytest.mark.auth
def test_deleted_user_cannot_authenticate(app, dbsession, client: TApp):
    """ deleted user -> cannot get token """
    data = {
        "email": "for_deletion@bar.io",
        "password": "12341234",
        "password_repeat": "12341234",
        "username": "for_deletion"
    }
    created_user_id = client.post_json('/api/register-user', data).json['data']['id']
    with app.app_context():
        created_user: User = UserRepository().get(created_user_id)
        created_user.is_deleted = True
        UserRepository().save(created_user)

    uid = uuid.uuid4()
    response = get_token_response(client, uid=uid, email=data['email'], status=401)
    print('response status code:', response.status_code)
    print('response json data:\n', response.json)
    assert response.json['uid'] == str(uid)
    assert response.json['status'] == ResponseStatus.AUTH_ERROR.value
    assert response.json['data'] is None


@pytest.mark.e2e
@pytest.mark.auth
@pytest.mark.parametrize(
    "email, password",
    [
        ('', 'jimmyh'),
        ('sas@kodzi.io', ''),
        ('   ', 'jimmyh'),
        ('sas@kodzi.io', '   '),
        (None, 'jimmyh'),
        ('sas@kodzi.io', None),
        ('wrong.email', 'xxx'),
        ('sas'*100, 'xxx')
    ]
)
def test_jwt_request_validation(client: TApp, email, password):
    """ test auth request validation """
    uid = uuid.uuid4()
    response = get_token_response(client, uid, email, password, status=400)
    print('response status code:', response.status_code)
    print('response json data:\n', response.json)

    assert response.json['uid'] == str(uid)
    assert response.json['status'] == ResponseStatus.VALIDATION_ERROR.value
    assert response.json['data'] is None
    assert len(response.json['errors']) > 0


@pytest.mark.e2e
@pytest.mark.auth
@pytest.mark.parametrize(
    "email, username",
    [
        ('foo@bar.io', 'jimmyh'),
        ('bar@foo.io', None),
    ]
)
def test_register_user(client: TApp, email, username):
    """ test registering user """
    data = {
        "uid": str(uuid.uuid4()),
        "email": email,
        "password": "12341234",
        "password_repeat": "12341234",
        "username": username
    }
    response = client.post_json('/api/register-user', data)

    print('response status code:', response.status_code)
    print('response json data:\n', response.json)
    assert response.json['uid'] == data['uid']
    assert response.json['status'] == 'OK'
    assert response.json['data']['id'] is not None
    assert response.json['data']['email'] == data['email']
    assert not response.json['data']['is_deleted']
    expected_groups = ('USER',)
    user_groups = [g['name'] for g in response.json['data']['groups']]
    for expected_group in expected_groups:
        assert expected_group in user_groups


@pytest.mark.e2e
@pytest.mark.auth
def test_delete_user(client: TApp, app, user, admin, superuser, get_headers):
    """ test user delete """
    new_user_data = {
        "email": "delete.me@later.io",
        "password": "12341234",
        "password_repeat": "12341234"
    }
    user_id = client.post_json('/api/register-user', new_user_data).json['data']['id']
    # regular user cannot delete
    client.post_json('/api/delete-user', {'user_id': user_id}, headers=get_headers('user'), status=403)
    # admin user can delete
    d = {
        "uid": str(uuid.uuid4()),
        "user_id": user_id
    }
    response = client.post_json('/api/delete-user', d, headers=get_headers('admin'))
    print('response status code:', response.status_code)
    print('response json data:\n', response.json)
    assert response.json['uid'] == d['uid']
    assert response.json['status'] == 'OK'
    assert response.json['data']['is_deleted']
    with app.app_context():
        assert UserRepository().get(user_id).is_deleted
    # su can delete
    client.post_json('/api/delete-user', {'user_id': user_id}, headers=get_headers('superuser'))


@pytest.mark.e2e
@pytest.mark.auth
@pytest.mark.debug
def test_get_user_data_user(client: TApp, app, user, admin, superuser, get_headers):
    """ test get user data """
    get_admin_data = {
        "uid": str(uuid.uuid4()),
        "user_id": admin.id
    }
    admin_data_response = client.post_json('/api/get-user-data', get_admin_data, headers=get_headers('user'))

    assert admin_data_response.json['uid'] == get_admin_data['uid']
    assert admin_data_response.json['status'] == 'OK'
    assert admin_data_response.json['data']['id'] == admin.id

    own_user_data = {}

    user_data_response = client.post_json('/api/get-user-data', own_user_data, headers=get_headers('user'))

    assert user_data_response.json['status'] == 'OK'
    assert user_data_response.json['data']['id'] == user.id
