import pytest

from db.model import User
from events.auth import RegisterUserEventHandler
from repository.repos import UserRepository


class DummyRequest:
    def __init__(self, json: dict):
        self.json = json


# noinspection PyTypeChecker
@pytest.mark.unit
@pytest.mark.model
def test_delete_user(app):
    """ test user deletion """
    with app.app_context():
        user_data = {
            'email': 'foo@bar.com',
            'password': 'deleteme',
            'password_repeat': 'deleteme'
        }
        uid = RegisterUserEventHandler(DummyRequest(user_data), validate=False)\
            .get_response().json['data']['id']

        repo = UserRepository()
        created_user: User = repo.get(uid)

        created_user.is_deleted = True
        repo.save(created_user)

        deleted_user: User = repo.get(uid)
        assert deleted_user.is_deleted

# todo: other tests
