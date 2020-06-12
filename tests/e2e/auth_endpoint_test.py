from flask.testing import FlaskClient


def test_auth(client: FlaskClient):
    response = client.post(
        '/api/token-auth',
        json={
            'email': 'jimmy@choo.io',
            'password': 'jimmyh'
        }
    )
    print('response', response)
    print('data', response.data)
    assert False
