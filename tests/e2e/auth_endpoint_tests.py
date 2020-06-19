import pytest
from webtest import TestApp as TApp

# ! important ! :: @pytest.mark.debug -> 4 debugging
from utils.http import ResponseStatus


def get_token_response(client: TApp, email: str, password: str, status: int = 200):
    return client.post_json(
        '/api/token-auth',
        {
            'email': email,
            'password': password
        },
        status=status
    )


@pytest.mark.e2e
@pytest.mark.parametrize("email,password", [('jimmy@choo.io', 'jimmyh'), ('sas@kodzi.io', 'sas')])
def test_get_jwt(client: TApp, email, password):
    """ test geting jwt token for admin and user """
    response = get_token_response(client, email, password)
    print('response status code:', response.status_code)
    print('response json data:\n', response.json)
    assert response.json['status'] == ResponseStatus.OK.value
    assert response.json['data']['token'] is not None


@pytest.mark.e2e
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
def test_register_user(client: TApp):
    """ test registering user """
    # parametrize two iterations
    data = {
        "email": "foo@bar.io",
        "password": "12341234",
        "password_repeat": "12341234",
        "username": "test"  # todo: with no username
    }
    response = client.post_json('/api/register-user', data)

    print('response status code:', response.status_code)
    print('response json data:\n', response.json)
    assert response.json['status'] == 'OK'
    assert response.json['data']['email'] == data['email']
    expected_groups = ('USER',)
    for expected_group in expected_groups:
        assert expected_group in response.json['data']['groups']


# todo: test invalid request -> validation
