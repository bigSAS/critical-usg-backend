import pytest
from webtest import TestApp as TApp
from tests.e2e.auth_endpoint_tests import get_token_response


@pytest.mark.e2e
@pytest.mark.parametrize("email,password", [('jimmy@choo.io', 'jimmyh'), ('sas@kodzi.io', 'sas')])
def test_todo_name_me(client: TApp, email, password):  # todo: tests
    """ ... """
    response = get_token_response(client, email, password)
    pass
    # print('response status code:', response.status_code)
    # print('response json data:\n', response.json)
    # assert response.json['status'] == ResponseStatus.OK.value
    # assert response.json['data']['token'] is not None
