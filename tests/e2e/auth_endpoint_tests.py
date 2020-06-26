import pytest
from webtest import TestApp as TApp

# ! important ! :: @pytest.mark.debug -> 4 debugging
from db.model import User
from repository.repos import UserRepository
from utils.http import ResponseStatus


def get_token_response(client: TApp, email: str, password: str = '12341234', status: int = 200):
    return client.post_json(
        '/api/token-auth',
        {
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
        response = get_token_response(client, usr.email)
        print('response status code:', response.status_code)
        print('response json data:\n', response.json)
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
        created_user = UserRepository().get(created_user_id)
        created_user.delete()
        dbsession.commit()

    response = get_token_response(client, data['email'], data['password'], status=401)
    print('response status code:', response.status_code)
    print('response json data:\n', response.json)
    assert response.json['status'] == ResponseStatus.AUTH_ERROR.value
    assert response.json['data'] is None


@pytest.mark.e2e
@pytest.mark.auth
@pytest.mark.parametrize(
    "email, password, expected_error_message",
    [
        ('', 'jimmyh', 'Field is required'),
        ('sas@kodzi.io', '', 'Field is required'),
        ('   ', 'jimmyh', 'Field is required'),
        ('sas@kodzi.io', '   ', 'Field is required'),
        (None, 'jimmyh', 'Field is required'),
        ('sas@kodzi.io', None, 'Field is required'),
        ('wrong.email', 'xxx', 'Email address is invalid'),
        ('sas'*100, 'xxx', 'Maximum length is 200')
    ]
)
def test_jwt_request_validation(client: TApp, email, password, expected_error_message: str):
    """ test auth request validation """
    response = get_token_response(client, email, password, status=400)
    print('response status code:', response.status_code)
    print('response json data:\n', response.json)
    assert response.json['status'] == ResponseStatus.VALIDATION_ERROR.value
    assert response.json['data'] is None
    errors = [err['message'] for err in response.json['errors']]
    assert expected_error_message in errors


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
        "email": email,
        "password": "12341234",
        "password_repeat": "12341234",
        "username": username
    }
    response = client.post_json('/api/register-user', data)

    print('response status code:', response.status_code)
    print('response json data:\n', response.json)
    assert response.json['status'] == 'OK'
    assert response.json['data']['email'] == data['email']
    assert not response.json['data']['is_deleted']
    expected_groups = ('USER',)
    for expected_group in expected_groups:
        assert expected_group in response.json['data']['groups']


@pytest.mark.e2e
@pytest.mark.auth
@pytest.mark.debug
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
    response = client.post_json('/api/delete-user', {'user_id': user_id}, headers=get_headers('admin'))
    print('response status code:', response.status_code)
    print('response json data:\n', response.json)
    assert response.json['status'] == 'OK'
    assert response.json['data']['is_deleted']
    with app.app_context():
        assert UserRepository().get(user_id).is_deleted
    # su can delete
    client.post_json('/api/delete-user', {'user_id': user_id}, headers=get_headers('superuser'))
