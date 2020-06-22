import pytest
from webtest import TestApp as TApp
from tests.e2e.auth_endpoint_tests import get_token_response


@pytest.mark.e2e
@pytest.mark.skip('not impl yet')
@pytest.mark.parametrize("email", ['jimmy@choo.io', 'sas@kodzi.io'])
def test_todo_name_me(client: TApp, email):  # todo: tests when event hanlder is done
    """ ... """
    response = get_token_response(client, email)
    pass
    # print('response status code:', response.status_code)
    # print('response json data:\n', response.json)
    # assert response.json['status'] == ResponseStatus.OK.value
    # assert response.json['data']['token'] is not None
