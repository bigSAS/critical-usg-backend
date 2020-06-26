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
def test_delete_user(app, dbsession):
    """ test user deletion """
    with app.app_context():
        user_data = {
            'email': 'foo@bar.com',
            'password': 'deleteme',
            'password_repeat': 'deleteme'
        }
        uid = RegisterUserEventHandler(DummyRequest(user_data), validate=False)\
            .get_response().json['data']['id']

        created_user: User = UserRepository().get(uid)

        created_user.delete()
        dbsession.commit()

        deleted_user: User =  UserRepository().get(uid)
        assert deleted_user.is_deleted

# todo: other tests
