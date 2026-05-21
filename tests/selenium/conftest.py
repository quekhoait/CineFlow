import pytest
import threading
import time
from werkzeug.serving import make_server
from selenium import webdriver
from app import create_app, db
from werkzeug.security import generate_password_hash
import uuid
from datetime import datetime, timedelta
from app.models import User, UserAuthMethod, RoleEnum, Cinema, Room, Seat, SeatType, Film, Show, Rules, Booking, Ticket, Payment


@pytest.fixture(scope="session")
def app_instance():
    app = create_app('testing')
    with app.app_context():
        db.drop_all()
        db.create_all()
        yield app
        db.session.remove()
        db.drop_all()

@pytest.fixture(scope="session")
def app_instance_v2():
    app = create_app('development')
    print(app.config['SQLALCHEMY_DATABASE_URI'])
    with app.app_context():
        yield app


@pytest.fixture(scope="session")
def local_server_url(app_instance):
    server = make_server('127.0.0.1', 8000, app_instance)
    server_thread = threading.Thread(target=server.serve_forever)
    server_thread.daemon = True
    server_thread.start()
    time.sleep(2)
    yield "http://127.0.0.1:8000"
    server.shutdown()
    server_thread.join()

@pytest.fixture(scope="session")
def local_server_url_v2(app_instance_v2):
    server = make_server('127.0.0.1', 5000, app_instance_v2)
    server_thread = threading.Thread(target=server.serve_forever)
    server_thread.daemon = True
    server_thread.start()
    time.sleep(2)
    yield "http://127.0.0.1:5000"
    server.shutdown()
    server_thread.join()


@pytest.fixture(scope="function")
def driver():
    options = webdriver.ChromeOptions()
    # options.add_argument('--headless')
    driver = webdriver.Chrome(options=options)
    driver.maximize_window()
    yield driver
    driver.quit()