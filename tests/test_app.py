import pytest
from flask import current_app

from app import create_app, db

@pytest.fixture(autouse=True)
def app_context():
    app = create_app('testing')
    app_context = app.app_context()
    app_context.push()
    db.create_all()

    yield app

    db.session.remove()
    db.drop_all()
    app_context.pop()

def test_app_exists():
    assert current_app is not None

def test_app_is_testing():
    assert current_app.config['TESTING']