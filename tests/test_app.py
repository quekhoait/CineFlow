from flask import current_app
from tests import BasicsTestCase

class AppTest(BasicsTestCase):
    def test_app_exists(self):
        self.assertTrue(current_app is not None)

    def test_app_is_testing(self):
        self.assertTrue(current_app.config['TESTING'])