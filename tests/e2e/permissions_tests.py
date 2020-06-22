import pytest
from webtest import TestApp as TApp

from tests.e2e.auth_endpoint_tests import get_token_response
from utils.http import ResponseStatus


@pytest.mark.e2e
@pytest.mark.permissions
@pytest.mark.skip('not impl yet')
def test_superuser_only_endpoint(client: TApp, user, superuser, get_headers):  # todo: impl <-
    """ test superuser protected endpoint - regular user should not have access """
    usr = user
    response = get_token_response(client, user.email, '12341234')
    print('response status code:', response.status_code)
    print('response json data:\n', response.json)
    assert response.json['status'] == ResponseStatus.OK.value
    assert response.json['data']['token'] is not None


@pytest.mark.e2e
@pytest.mark.permissions
@pytest.mark.skip('not impl yet')
def test_group_only_endpoint(client: TApp, user, superuser, get_headers):  # todo: impl <-
    """ test user group protected endpoint - user should not have access when not belong to group """
    usr = user
    response = get_token_response(client, user.email, '12341234')
    print('response status code:', response.status_code)
    print('response json data:\n', response.json)
    assert response.json['status'] == ResponseStatus.OK.value
    assert response.json['data']['token'] is not None


@pytest.mark.e2e
@pytest.mark.permissions
@pytest.mark.skip('not impl yet')
def test_open_endpoint(client: TApp, user, superuser, get_headers):  # todo: impl <-
    """ test open endpoint - all have access """
    usr = user
    response = get_token_response(client, user.email, '12341234')
    print('response status code:', response.status_code)
    print('response json data:\n', response.json)
    assert response.json['status'] == ResponseStatus.OK.value
    assert response.json['data']['token'] is not None
