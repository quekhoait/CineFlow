import pytest
from sqlalchemy.exc import IntegrityError
from faker import Faker
from app.models.user import User, RoleEnum

fake = Faker('vi_VN')


class TestUserModel:
    def test_user_creation_default_values(self, test_session):
        new_user = User(
            username=fake.user_name(),
            email=fake.email(),
            phone_number=fake.phone_number()[:15]
        )
        test_session.add(new_user)
        test_session.commit()

        saved_user = test_session.query(User).filter_by(username=new_user.username).first()

        assert saved_user.role == RoleEnum.USER
        assert saved_user.is_active is True
        assert saved_user.avatar == '/static/image/icon_user.png'

    @pytest.mark.parametrize("missing_field", ["username"])
    def test_user_missing_required_fields(self, test_session, missing_field):
        user_data = {
            "username": fake.user_name(),
            "email": fake.email()
        }
        user_data.pop(missing_field)

        invalid_user = User(**user_data)
        test_session.add(invalid_user)

        with pytest.raises(IntegrityError):
            test_session.commit()
        test_session.rollback()

    def test_user_unique_constraints(self, test_session):
        shared_email = fake.email()
        shared_username = fake.user_name()

        user1 = User(username=shared_username, email=shared_email)
        test_session.add(user1)
        test_session.commit()

        user2 = User(username=shared_username, email=fake.email())
        test_session.add(user2)

        with pytest.raises(IntegrityError):
            test_session.commit()
        test_session.rollback()