import pytest
from webtest import TestApp as TApp

from application import apk


@pytest.fixture
def client() -> TApp:
    yield TApp(apk)
