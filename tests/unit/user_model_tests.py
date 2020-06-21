import pytest

from db.model import User
from events.auth import RegisterUserEventHandler


class DummyRequest:
    def __init__(self, json: dict):
        self.json = json


@pytest.mark.unit
@pytest.mark.debug
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

        created_user: User = dbsession.query(User).filter_by(id=uid).first()
        created_user.delete()
        dbsession.commit()

        deleted_user: User = dbsession.query(User).filter_by(id=uid).first()
        assert deleted_user.is_deleted

