import pytest
from webtest import TestApp as TApp

from utils.http import ResponseStatus


@pytest.mark.e2e
@pytest.mark.permissions
def test_superuser_only_endpoint(client: TApp, user, admin, superuser, get_headers):
    """ test superuser protected endpoint - regular user should not have access """

    # superuser -> should be ok
    response = client.post_json('/api/superuser-ping', {}, headers=get_headers('superuser'))
    print('response status code:', response.status_code)
    print('response json data:\n', response.json)
    assert response.status_code == 200
    assert response.json['msg'] == 'super!'

    # user -> should be 403
    response = client.post_json('/api/superuser-ping', {}, headers=get_headers('user'), status=403)
    print('response status code:', response.status_code)
    print('response json data:\n', response.json)
    assert response.status_code == 403
    assert response.json['status'] == ResponseStatus.FORBIDDEN.value
    assert response.json['data'] is None

    # admin -> should be 403
    response = client.post_json('/api/superuser-ping', {}, headers=get_headers('admin'), status=403)
    print('response status code:', response.status_code)
    print('response json data:\n', response.json)
    assert response.status_code == 403
    assert response.json['status'] == ResponseStatus.FORBIDDEN.value
    assert response.json['data'] is None


@pytest.mark.e2e
@pytest.mark.permissions
def test_group_only_endpoint(client: TApp, user, admin, superuser, get_headers):
    """ test user group protected endpoint - user should not have access when not belong to group """
    # user -> should be ok
    response = client.post_json('/api/user-ping', {}, headers=get_headers('user'))
    print('response status code:', response.status_code)
    print('response json data:\n', response.json)
    assert response.status_code == 200
    assert response.json['msg'] == 'pong!'

    # superuser -> should be ok
    response = client.post_json('/api/user-ping', {}, headers=get_headers('superuser'))
    print('response status code:', response.status_code)
    print('response json data:\n', response.json)
    assert response.status_code == 200
    assert response.json['msg'] == 'pong!'

    # admin -> should be forbidden
    response = client.post_json('/api/user-ping', {}, headers=get_headers('admin'), status=403)
    print('response status code:', response.status_code)
    print('response json data:\n', response.json)
    assert response.status_code == 403
    assert response.json['status'] == ResponseStatus.FORBIDDEN.value
    assert response.json['data'] is None


@pytest.mark.e2e
@pytest.mark.permissions
# @pytest.mark.debug
def test_open_endpoint(client: TApp, user, admin, superuser, get_headers):
    """ test open endpoint - all have access """
    # no user -> should be ok
    response = client.post_json('/api/open-ping', {})
    print('response status code:', response.status_code)
    print('response json data:\n', response.json)
    assert response.status_code == 200
    assert response.json['msg'] == 'hello!'

    # user -> should be ok
    response = client.post_json('/api/open-ping', {}, headers=get_headers('user'))
    print('response status code:', response.status_code)
    print('response json data:\n', response.json)
    assert response.status_code == 200
    assert response.json['msg'] == 'hello!'

    # admin -> should be ok
    response = client.post_json('/api/open-ping', {}, headers=get_headers('admin'))
    print('response status code:', response.status_code)
    print('response json data:\n', response.json)
    assert response.status_code == 200
    assert response.json['msg'] == 'hello!'

    # superuser -> should be ok
    response = client.post_json('/api/open-ping', {}, headers=get_headers('superuser'))
    print('response status code:', response.status_code)
    print('response json data:\n', response.json)
    assert response.status_code == 200
    assert response.json['msg'] == 'hello!'
