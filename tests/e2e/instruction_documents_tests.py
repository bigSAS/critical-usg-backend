import uuid
from json import dumps

import pytest
from webtest import TestApp as TApp

from db.schema import InstructionDocument, InstructionDocumentPage
from repository.repos import InstructionDocumentRepository
from utils.http import ResponseStatus
from utils.managers import InstructionDocumentManager


@pytest.mark.e2e
@pytest.mark.docs
@pytest.mark.parametrize("description", [". . .", None])
def test_creates_new_doc(client: TApp, user, admin, get_headers, description):
    """ corret doc creation by admin user """
    data = {
        'uid': str(uuid.uuid4()),
        'name': 'some cool new doc',
        'description': description
    }
    # admin can create
    response = client.post_json('/api/instruction-documents/add-doc', data, headers=get_headers('admin'))
    print('response status code:', response.status_code)
    print('response json data:\n', response.json)
    assert response.json['status'] == ResponseStatus.OK.value
    assert response.json['uid'] == data['uid']
    assert response.json['data']['created'] is not None
    assert response.json['data']['created_by_user_id'] == admin.id
    assert response.json['data']['name'] == data['name']
    assert response.json['data']['description'] == data['description']
    assert response.json['data']['updated_by_user_id'] is None
    assert response.json['data']['updated'] is None

    # user cannot create
    client.post_json('/api/instruction-documents/add-doc', data, headers=get_headers('user'), status=403)


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
        'uid': str(uuid.uuid4()),
        'document_id': created_doc_id
    }
    # admin can delete
    res = client.post_json('/api/instruction-documents/delete-doc', delete_doc_data, headers=get_headers('admin'))
    assert res.json['status'] == 'OK'
    assert res.json['uid'] == delete_doc_data['uid']
    assert res.json['data'] is None
    # user cannnot delete
    client.post_json('/api/instruction-documents/delete-doc', delete_doc_data, headers=get_headers('user'), status=403)


@pytest.mark.e2e
@pytest.mark.docs
@pytest.mark.parametrize(
    "user_type, description",
    [
        ('admin', 'new desc'),
        ('admin', None),
    ]
)
def test_updates_doc(client: TApp, admin, get_headers, user_type, description):
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
        'uid': str(uuid.uuid4()),
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
    assert response.json['uid'] == update_doc_data['uid']
    assert response.json['data']['id'] == update_doc_data['document_id']
    assert response.json['data']['name'] == update_doc_data['name']
    assert response.json['data']['description'] == update_doc_data['description']
    assert response.json['data']['updated_by_user_id'] == admin.id
    assert response.json['data']['updated'] is not None


@pytest.mark.e2e
@pytest.mark.docs
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
        "uid": str(uuid.uuid4()),
        "document_id": created_doc_id,
        "json_data": dumps({
            "bar": "baz"
        })
    }

    response = client.post_json(
        '/api/instruction-documents/add-page',
        doc_pages_data,
        headers=get_headers('admin')
    )
    assert response.json['status'] == 'OK'
    assert response.json['uid'] == doc_pages_data['uid']
    assert response.json['data']['id'] is not None
    assert response.json['data']['document_id'] == created_doc_id
    assert response.json['data']['json_data'] == doc_pages_data['json_data']
    with app.app_context():
        doc: InstructionDocument = InstructionDocumentRepository().get(created_doc_id)
        assert doc.updated_by_user_id == admin.id
        assert doc.updated is not None
        magaged_doc = InstructionDocumentManager(document=doc)
        assert magaged_doc.page_count() == 1


@pytest.mark.e2e
@pytest.mark.docs
def test_updates_doc_page(app, client: TApp, admin, get_headers):
    """ corret doc page edittion """
    create_doc_data = {
        "name": "doc with pages to update",
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

    page_id = client.post_json(
        '/api/instruction-documents/add-page',
        doc_pages_data,
        headers=get_headers('admin')
    ).json['data']['id']
    update_page_data = {
        "page_id": page_id,
        "json": {
            "cool": "update"
        }
    }

    response = client.post_json(
        '/api/instruction-documents/update-page',
        update_page_data,
        headers=get_headers('admin')
    )

    assert response.json['status'] == 'OK'
    assert response.json['data']['json'] == update_page_data['json']
    with app.app_context():
        doc: InstructionDocument = InstructionDocumentRepository().get(created_doc_id)
        assert doc.updated_by_user_id == admin.id
        assert doc.updated is not None


@pytest.mark.e2e
@pytest.mark.docs
def test_deletes_doc_page(app, client: TApp, admin, user, get_headers):
    """ corret doc page deletion """
    create_doc_data = {
        "name": "doc with pages to delete",
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

    page_id = client.post_json(
        '/api/instruction-documents/add-page',
        doc_pages_data,
        headers=get_headers('admin')
    ).json['data']['id']
    with app.app_context():
        doc: InstructionDocument = InstructionDocumentRepository().get(created_doc_id)
        assert doc.updated_by_user_id == admin.id
        assert doc.updated is not None
        magaged_doc = InstructionDocumentManager(document=doc)
        assert magaged_doc.page_count() == 1

    deletion_data = {
        "page_id": page_id
    }

    response = client.post_json(
        '/api/instruction-documents/delete-page',
        deletion_data,
        headers=get_headers('admin')
    )
    assert response.json['status'] == 'OK'
    assert response.json['data'] is None

    with app.app_context():
        doc: InstructionDocument = InstructionDocumentRepository().get(created_doc_id)
        assert doc.updated_by_user_id == admin.id
        assert doc.updated is not None
        magaged_doc = InstructionDocumentManager(document=doc)
        assert magaged_doc.page_count() == 0


@pytest.mark.e2e
@pytest.mark.docs
def test_lists_docs(app, client: TApp, admin, user, get_headers):
    """ corret doc listing """
    with app.app_context():
        repo = InstructionDocumentRepository()
        for i in range(1, 10):
            repo.save(InstructionDocument(
                f'[{i}]test doc',
                'foo',
                admin
            ))

    list_docs_data = {
        "page": 2,
        "limit": 3
    }
    response = client.post_json(
        '/api/instruction-documents/list-docs',
        list_docs_data,
        headers=get_headers('nouser'))

    assert response.json['status'] == 'OK'
    assert response.json['data']['page'] == list_docs_data['page']
    assert response.json['data']['prev_num'] == list_docs_data['page'] - 1
    assert response.json['data']['next_num'] == list_docs_data['page'] + 1
    assert len(response.json['data']['results']) == 3


@pytest.mark.e2e
@pytest.mark.docs
def test_search_docs(app, client: TApp, admin, user, get_headers):
    """ corret doc searching """
    added_count = 0
    with app.app_context():
        repo = InstructionDocumentRepository()
        for i in range(1, 10):
            repo.save(InstructionDocument(
                f'[{i}] searched doc',
                'foo',
                admin
            ))
            added_count += 1
        for i in range(1, 6):
            repo.save(InstructionDocument(
                f'[{i}] ...',
                f'xyz {i} searched doc',
                admin
            ))
            added_count += 1

    search_docs_data = {
        "search": "SearChed dOc",
        "page": 1,
        "limit": 100
    }
    response = client.post_json(
        '/api/instruction-documents/search-docs',
        search_docs_data,
        headers=get_headers('nouser'))

    assert response.json['status'] == 'OK'
    assert response.json['data']['page'] == 1
    assert len(response.json['data']['results']) == added_count
    pass


@pytest.mark.e2e
@pytest.mark.docs
def test_gets_doc(app, client: TApp, admin, user, get_headers):
    """ corret doc getting """
    page_json = {"foo": "bar"}
    with app.app_context():
        repo = InstructionDocumentRepository()
        doc = InstructionDocument(
            f'coolish doc',
            '. . .',
            admin
        )
        managed_doc = InstructionDocumentManager(document=doc)
        repo.save(doc)
        page = InstructionDocumentPage(
            document_id=doc.id,
            json=page_json
        )
        managed_doc.add_page(page, admin.id)
        doc_id = doc.id

    get_doc_data = {
        "document_id": doc_id
    }
    response = client.post_json(
        '/api/instruction-documents/get-doc',
        get_doc_data,
        headers=get_headers('nouser'))

    assert response.json['status'] == 'OK'
    assert len(response.json['data']['pages']) == 1
    assert response.json['data']['pages'][0]['page_num'] == 1
    assert response.json['data']['pages'][0]['document_id'] == doc_id
    assert response.json['data']['pages'][0]['json'] == page_json
