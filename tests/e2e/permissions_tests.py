import pytest
from webtest import TestApp as TApp

from tests.e2e.auth_endpoint_tests import get_token_response
from utils.http import ResponseStatus


@pytest.mark.e2e
@pytest.mark.skip('not impl yet')
def test_get_jwt(client: TApp, user, admin, get_headers):  # todo: impl <-
    """ test admin protected endpoint - user should not have access """
    usr = user
    response = get_token_response(client, user.email, '12341234')
    print('response status code:', response.status_code)
    print('response json data:\n', response.json)
    assert response.json['status'] == ResponseStatus.OK.value
    assert response.json['data']['token'] is not None
