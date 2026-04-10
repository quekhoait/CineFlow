import uuid

from parameterized import parameterized
from flask_jwt_extended import create_refresh_token
from werkzeug.security import generate_password_hash, check_password_hash
from app import models, db
from app.dto.user_dto import RegisterRequest, GoogleAuthRequest, UserAuthMethodRequest
from app.repository import user_repo
from app.repository.user_repo import create_user_auth_method
from tests import BasicsTestCase

class UserRepoTest(BasicsTestCase):
    def sample_data(self):
        for i in range(1,13):
            u = models.User(id=i,username=f'u{i}', password=generate_password_hash('Admin123@'), full_name=f'u{i}',email=f'u{i}@gmail.com',role=models.RoleEnum.USER,is_active=True)
            db.session.add(u)
            if i in range(5):
                u_method = models.UserAuthMethod(id=i, user_id=i, provider="EMAIL", provider_id=f'u{i}@gmail.com', refresh_token=create_refresh_token(str(i)))
                db.session.add(u_method)
            elif i in range(5,12):
                u_method = models.UserAuthMethod(id=i, user_id=i, provider="GOOGLE", provider_id=f'{100000+i}',refresh_token=create_refresh_token(str(i)))
                db.session.add(u_method)

            if i==12:
                u_method = models.UserAuthMethod(id=i, user_id=i, provider="EMAIL", provider_id=f'u{i}@gmail.com',
                                                 refresh_token=create_refresh_token(str(i)))
                db.session.add(u_method)
                i = i + 1
                u_method = models.UserAuthMethod(id=i, user_id=i-1, provider="GOOGLE", provider_id=f'{100000 + i-1}',
                                                 refresh_token=create_refresh_token(str(i-1)))
                db.session.add(u_method)

        db.session.commit()

    def setUp(self):
        super().setUp()
        self.sample_data()

    @parameterized.expand([
        (1, {"id":1,"username":"u1","password":generate_password_hash('Admin123@'), "full_name":"u1","email":"u1@gmail.com", "role":models.RoleEnum.USER, "is_active":True}),
        (0, None),
        (11, {"id": 11, "username": "u11", "password": generate_password_hash('Admin123@'), "full_name": "u11","email": "u11@gmail.com", "role": models.RoleEnum.USER, "is_active": True}),
        (199, None)
    ])
    def test_get_user_by_user_id(self, user_id, expected):
        user = user_repo.get_user_by_user_id(user_id)
        if expected is None:
            self.assertIsNone(user)
        else:
            self.assertIsNotNone(user)
            self.assertEqual(user.id, expected["id"])
            self.assertEqual(user.username, expected["username"])
            self.assertEqual(user.full_name, expected["full_name"])
            self.assertTrue(check_password_hash(user.password, 'Admin123@'))

    @parameterized.expand([
        ("u1@gmail.com", {"id": 1, "username": "u1", "password": generate_password_hash('Admin123@'), "full_name": "u1",
             "email": "u1@gmail.com", "role": models.RoleEnum.USER, "is_active": True}),
        ("u999@gmail.com", None),
        ("u11@gmail.com", {"id": 11, "username": "u11", "password": generate_password_hash('Admin123@'), "full_name": "u11",
              "email": "u11@gmail.com", "role": models.RoleEnum.USER, "is_active": True}),
    ])
    def test_get_user_by_email(self, email, expected):
        user = user_repo.get_user_by_email(email)
        if expected is None:
            self.assertIsNone(user)
        else:
            self.assertIsNotNone(user)
            self.assertEqual(user.id, expected["id"])
            self.assertEqual(user.username, expected["username"])
            self.assertEqual(user.full_name, expected["full_name"])
            self.assertTrue(check_password_hash(user.password, 'Admin123@'))

    @parameterized.expand([
        ("u1@gmail.com", 1),
        ("u999", None),
        ("u11@gmail.com", 11),
    ])
    def test_get_user_id_by_email(self, email, expected):
        user_id = user_repo.get_user_id_by_email(email)
        if expected is None:
            self.assertIsNone(user_id)
        else:
            self.assertIsNotNone(user_id)
            self.assertEqual(user_id, expected)

    @parameterized.expand([
        ("u1", 1),
        ("balaba", None),
        ("u11", 11),
    ])
    def test_get_user_id_by_username(self, username, expected):
        user_id = user_repo.get_user_id_by_username(username)
        if expected is None:
            self.assertIsNone(user_id)
        else:
            self.assertIsNotNone(user_id)
            self.assertEqual(user_id, expected)

    @parameterized.expand([
        ("u1@gmail.com", 1),
        ("u4@gmail.com", 4),
        ("100012", 12),
        ("100011", 11),
        ("100000121", None),

    ])
    def test_get_user_id_by_provider_id(self, provider_id, expected):
        user_id = user_repo.get_user_id_by_provider_id(provider_id)
        if expected is None:
            self.assertIsNone(user_id)
        else:
            self.assertIsNotNone(user_id)
            self.assertEqual(user_id, expected)

    @parameterized.expand([
        ({"email": "test1@example.com", "password":"Abc123@", "username":"Utest1", "full_name":"User One", "phone_number":"0244685795", "avatar":"url_1", "otp":"1111"},),
        ({"email": "test2@example.com", "password": "Abc123@", "username": "Utest2", "full_name": "User Two", "avatar": "url_1",  "otp":"1111"},),
        ({"email": "test3@example.com", "password": "Abc123@", "username": "Utest3", "full_name": "User Three", "phone_number": "0244685795",  "otp":"1111"},),
        ({"email": "test4@example.com", "password": "Abc123@", "username": "Utest4", "full_name": "User Four",  "otp":"1111"},),
    ])
    def test_create_user_email(self, request):
        req = RegisterRequest().load(request)
        new_user = user_repo.create_user_email(req)
        db.session.commit()
        self.assertIsNotNone(new_user)
        self.assertIsNotNone(new_user.id)
        self.assertEqual(new_user.email, req.email)
        self.assertEqual(new_user.username, req.username)
        self.assertEqual(new_user.full_name, req.full_name)
        self.assertEqual(new_user.password, req.password)

    @parameterized.expand([
        ({'sub': '11516295363766329', 'name': 'TestGoogle1', 'given_name': 'test',  'picture': 'url_1', 'email': 'testgg01@gmail.com'},)
    ])
    def test_create_user_google(self, request):
        req = GoogleAuthRequest().load(request)
        new_user = user_repo.create_user_google(req)
        self.assertIsNotNone(new_user)
        db.session.commit()
        self.assertIsNotNone(new_user.id)
        self.assertEqual(new_user.email, req.email)
        self.assertEqual(new_user.username, req.username)
        self.assertEqual(new_user.full_name, req.full_name)
        self.assertEqual(new_user.avatar, req.avatar)

        auth = UserAuthMethodRequest().load({
            "user_id": new_user.id,
            "provider_id": req.provider_id,
            "provider": req.provider,
        })
        auth_method = create_user_auth_method(auth)
        self.assertIsNotNone(auth_method)
        self.assertIsNotNone(auth_method.id)
        self.assertEqual(auth_method.user_id, new_user.id)
        self.assertEqual(auth_method.provider_id, auth.provider_id)
        self.assertEqual(auth_method.provider, auth.provider)

    @parameterized.expand([
        (1, "23467892348"),
        (1, "23467892834"),
        (6, "67489038764")
    ])
    def test_update_user_auth_method(self, user_id, refresh_token):
        auth_method = user_repo.update_user_auth_method(user_id, refresh_token)
        self.assertIsNotNone(auth_method)
        self.assertIsNotNone(auth_method.id)
        self.assertEqual(auth_method.user_id, user_id)
        self.assertEqual(auth_method.refresh_token, refresh_token)
