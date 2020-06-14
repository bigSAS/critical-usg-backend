from webtest import TestApp as TApp


def test_auth(client: TApp):
    response = client.post_json(
        '/api/token-auth',
        {
            'email': 'jimmy@choo.io',
            'password': 'jimmyh'
        }
    )
    print('response', response)
    print('data', response.json)
    assert False  # todo assertion
