import pytest
from webtest import TestApp as TApp

# ! important ! :: @pytest.mark.debug -> 4 debugging


@pytest.mark.e2e
@pytest.mark.parametrize("email,password", [('jimmy@choo.io', 'jimmyh'), ('sas@kodzi.io', 'sas')])
def test_get_jwt(client: TApp, email, password):
    """ test geting jwt token for admin and user """
    response = client.post_json(
        '/api/token-auth',
        {
            'email': email,
            'password': password
        }
    )
    print('response status code:', response.status_code)
    print('response json data:\n', response.json)
    assert response.json['data']['token'] is not None


@pytest.mark.e2e
@pytest.mark.parametrize("user_type", ['user', 'admin'])
def test_token_ping_with_jwt(client: TApp, get_headers, user_type):
    """ test getting headers for authorized endpoint """
    response = client.get(
        '/api/token-ping',
        headers=get_headers(user_type)
    )
    print('response status code:', response.status_code)
    print('response json data:\n', response.json)
    assert response.json['msg'] == 'pong!'
