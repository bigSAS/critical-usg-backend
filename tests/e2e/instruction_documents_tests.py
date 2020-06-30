import pytest
from webtest import TestApp as TApp

from db.model import InstructionDocument
from repository.repos import InstructionDocumentRepository
from utils.http import ResponseStatus


@pytest.mark.e2e
@pytest.mark.docs
@pytest.mark.parametrize("description", [". . .", None])
def test_creates_new_doc(client: TApp, user, admin, get_headers, description):
    """ corret doc creation by admin user """
    data = {
        'name': 'some cool new doc',
        'description': description
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
def test_deletes_doc(client: TApp, admin, user, get_headers):
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


@pytest.mark.e2e
@pytest.mark.docs
@pytest.mark.parametrize(
    "user_type, description",
    [
        ('admin', 'new desc'),
        ('user', 'new desc'),
        ('admin', None),
        ('user', None),
    ]
)
def test_updates_doc(client: TApp, admin, user, get_headers, user_type, description):
    """ correct document object update """
    create_doc_data = {
        'name': 'some cool new doc fo edition',
        'description': '. . .'
    }
    created_doc_id = client.post_json(
        '/api/instruction-documents/add-doc',
        create_doc_data,
        headers=get_headers('admin')).json['data']['id']

    assert created_doc_id is not None
    update_doc_data = {
        'document_id': created_doc_id,
        'name': 'new name',
        'description': description
    }
    # admin can update
    response = client.post_json(
        '/api/instruction-documents/update-doc',
        update_doc_data,
        headers=get_headers(user_type))
    assert response.json['status'] == 'OK'
    assert response.json['data']['id'] == update_doc_data['document_id']
    assert response.json['data']['name'] == update_doc_data['name']
    assert response.json['data']['description'] == update_doc_data['description']
    assert response.json['data']['updated_by']['id'] == admin.id if user_type == 'admin' else user.id
    assert response.json['data']['updated'] is not None

# todo: other tests -> validation etc


@pytest.mark.e2e
@pytest.mark.docs
@pytest.mark.debug
def test_adds_doc_page(app, client: TApp, admin, user, get_headers):
    """ corret doc page addition """
    create_doc_data = {
        "name": "doc with pages",
        "description": "..."
    }
    created_doc_id = client.post_json(
        '/api/instruction-documents/add-doc',
        create_doc_data,
        headers=get_headers('admin')).json['data']['id']

    assert created_doc_id is not None
    doc_pages_data = {
        "document_id": created_doc_id,
        "json": {
            "bar": "baz"
        }
    }

    response = client.post_json(
        '/api/instruction-documents/add-page',
        doc_pages_data,
        headers=get_headers('admin')
    )
    assert response.json['status'] == 'OK'
    assert response.json['data']['id'] is not None
    assert response.json['data']['document_id'] == created_doc_id
    assert response.json['data']['json'] == doc_pages_data['json']
    with app.app_context():
        doc: InstructionDocument = InstructionDocumentRepository().get(created_doc_id)
        assert doc.updated_by_user_id == admin.id
        assert doc.updated is not None
