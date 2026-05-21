# import threading
# import time
# import pytest
# from selenium import webdriver
# from app import create_app, db
# from werkzeug.security import generate_password_hash
# import uuid
# from datetime import datetime, timedelta
# from app.models import User, UserAuthMethod, RoleEnum, Cinema, Room, Seat, SeatType, Film, Show, Rules, Booking, Ticket, Payment
#
#
# @pytest.fixture(scope="session")
# def app_instance():
#     app = create_app('testing')
#     print(app.config['SQLALCHEMY_DATABASE_URI'])
#     print(app.config['SQLALCHEMY_DATABASE_URI'])
#     with app.app_context():
#         db.drop_all()
#         db.create_all()
#         yield app
#         db.session.remove()
#         db.drop_all()
#
# @pytest.fixture(scope="session")
# def local_server_url(app_instance):
#     server_thread = threading.Thread(
#         target=lambda: app_instance.run(host='127.0.0.1', port=5000, use_reloader=False, debug=False)
#     )
#     server_thread.daemon = True
#     server_thread.start()
#     time.sleep(2)
#     return "http://127.0.0.1:5000"
#     # return "https://www.ndhuwng05.me/"
#
# @pytest.fixture
# def driver():
#     options = webdriver.ChromeOptions()
#     # options.add_argument('--headless')
#     driver = webdriver.Chrome(options=options)
#     driver.maximize_window()
#     yield driver
#     driver.quit()
#
