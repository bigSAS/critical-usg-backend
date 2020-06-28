import pytest
from webtest import TestApp as TApp

from utils.http import ResponseStatus


@pytest.mark.e2e
@pytest.mark.docs
def test_admin_creates_new_doc(client: TApp, user, admin, get_headers):
    """ corret doc creation by admin user """
    data = {
        'name': 'some cool new doc',
        'description': '. . .'
    }
    # admin can create
    response = client.post_json('/api/instruction-documents/add-doc', data, headers=get_headers('admin'))
    print('response status code:', response.status_code)
    print('response json data:\n', response.json)
    assert response.json['status'] == ResponseStatus.OK.value
    assert response.json['data']['created_by']['id'] == admin.id
    assert response.json['data']['name'] == data['name']
    assert response.json['data']['description'] == data['description']
    assert response.json['data']['updated_by'] is None
    assert response.json['data']['updated'] is None

    # user cannot create
    client.post_json('/api/instruction-documents/add-doc', data, headers=get_headers('user'), status=403)


# todo: other tests (validation etc)

@pytest.mark.e2e
@pytest.mark.docs
@pytest.mark.debug
def test_admin_delete_doc(client: TApp, admin, user, get_headers):
    """ corret doc deletion by admin user """
    create_doc_data = {
        'name': 'some cool new doc fo deletion',
        'description': '. . .'
    }
    created_doc_id = client.post_json(
        '/api/instruction-documents/add-doc',
        create_doc_data,
        headers=get_headers('admin')).json['data']['id']

    assert created_doc_id is not None
    delete_doc_data = {
        'document_id': created_doc_id
    }
    # admin can delete
    client.post_json('/api/instruction-documents/delete-doc', delete_doc_data, headers=get_headers('admin'))
    # user cannnot delete
    client.post_json('/api/instruction-documents/delete-doc', delete_doc_data, headers=get_headers('user'), status=403)


# todo: other tests -> validation etc
