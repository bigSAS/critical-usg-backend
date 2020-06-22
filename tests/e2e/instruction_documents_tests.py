import pytest
from webtest import TestApp as TApp

from utils.http import ResponseStatus


@pytest.mark.e2e
@pytest.mark.docs
def test_admin_creates_new_doc(client: TApp, admin, get_headers):
    """ corret doc creation by admin user """
    data = {
        'name': 'some cool new doc',
        'description': '. . .'
    }
    response = client.post_json('/api/instruction-documents/add-doc', data, headers=get_headers('admin'))
    print('response status code:', response.status_code)
    print('response json data:\n', response.json)
    assert response.json['status'] == ResponseStatus.OK.value
    assert response.json['data']['created_by']['id'] == admin.id
    assert response.json['data']['name'] == data['name']
    assert response.json['data']['description'] == data['description']
    assert response.json['data']['updated_by'] is None
    assert response.json['data']['updated'] is None


# todo: other tests
