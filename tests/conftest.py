import uuid
import pytest
from flask import Flask
from faker import Faker
import threading
import time
from app import create_app, db
from app.models import *
from flask_jwt_extended import JWTManager
from sqlalchemy import event

fake = Faker('vi_VN')
collect_ignore_glob = ["selenium/*"]

def create_test_app():
    app = create_app('testing')
    app.config["PAGE_SIZE"] = 2
    app.config["JWT_SECRET_KEY"] = "test-secret-key"
    JWTManager(app)
    return app


def _enable_sqlite_foreign_keys(engine):
    if engine.dialect.name != "sqlite":
        return

    @event.listens_for(engine, "connect")
    def _set_sqlite_pragma(dbapi_connection, connection_record):
        cursor = dbapi_connection.cursor()
        cursor.execute("PRAGMA foreign_keys=ON")
        cursor.close()


@pytest.fixture(scope="session", autouse=True)
def _prepare_test_database():
    app = create_test_app()
    with app.app_context():
        _enable_sqlite_foreign_keys(db.engine)
        db.session.remove()
        db.drop_all()
        db.create_all()
    yield
    with app.app_context():
        db.session.remove()
        db.drop_all()

@pytest.fixture(scope="session")
def test_app():
    app = create_test_app()
    with app.app_context():
        _enable_sqlite_foreign_keys(db.engine)
        db.session.remove()
        db.drop_all()
        db.create_all()
        yield app
        db.drop_all()

@pytest.fixture(scope="function")
def test_session(test_app):
    connection = db.engine.connect()
    transaction = connection.begin()
    session = db._make_scoped_session(options={"bind": connection, "binds": {}})
    db.session = session
    yield session

    session.close()
    transaction.rollback()
    connection.close()

@pytest.fixture
def test_setup_user(test_session):

    unique_suffix = str(uuid.uuid4())[:6]

    user = User(
        username=f"{fake.user_name()}_{unique_suffix}",
        email=f"{unique_suffix}_{fake.email()}",
        phone_number=fake.phone_number()[:15]
    )
    test_session.add(user)
    test_session.commit()
    return user

@pytest.fixture
def test_setup_cinema_and_room(test_session):
    cinema = Cinema(name=fake.company(), address=fake.address())
    test_session.add(cinema)
    test_session.commit()
    room = Room(name="Room 1", cinema_id=cinema.id)
    test_session.add(room)
    test_session.commit()
    return room



# @pytest.fixture
# def client(test_app):
#     return test_app.test_client()
#
# @pytest.fixture
# def mock_jwt(mocker):
#     mocker.patch('flask_jwt_extended.view_decorators.verify_jwt_in_request', return_value=None)
#     mocker.patch('flask_jwt_extended.utils.get_jwt_identity', return_value=4)
#     mocker.patch('flask_jwt_extended.utils.get_jwt', return_value={'sub': 4})


