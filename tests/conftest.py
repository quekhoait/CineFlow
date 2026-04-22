import uuid

import pytest
from flask import Flask
from faker import Faker
from app import db
from app.api import api as api_blueprint
from app.models.cinema import Cinema, Room
from app.models.user import User

fake = Faker('vi_VN')

def create_test_app():
    app = Flask(__name__)
    app.config["SQLALCHEMY_DATABASE_URI"] = "mysql+pymysql://root:root@localhost/cineflow"
    app.config["TESTING"] = True
    app.config["PAGE_SIZE"] = 2
    app.register_blueprint(api_blueprint)
    db.init_app(app)
    return app

@pytest.fixture(scope="session")
def test_app():
    app = create_test_app()
    with app.app_context():
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