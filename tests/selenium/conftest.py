import threading
import time
import pytest
from selenium import webdriver
from app import create_app, db


@pytest.fixture(scope="session")
def app_instance():
    app = create_app('testing')
    print(app.config['SQLALCHEMY_DATABASE_URI'])

    with app.app_context():
        db.drop_all()
        db.create_all()
        yield app
        db.session.remove()
        db.drop_all()

@pytest.fixture(scope="session")
def local_server_url(app_instance):
    server_thread = threading.Thread(
        target=lambda: app_instance.run(host='127.0.0.1', port=8000, use_reloader=False, debug=False)
    )
    server_thread.daemon = True
    server_thread.start()
    time.sleep(2)
    return "http://127.0.0.1:8000"

@pytest.fixture
def driver():
    options = webdriver.ChromeOptions()
    # options.add_argument('--headless')
    driver = webdriver.Chrome(options=options)
    driver.maximize_window()
    yield driver
    driver.quit()