import time
import pytest
from selenium.webdriver.common.by import By
from werkzeug.security import generate_password_hash
from app import db, cache
from app.models import User, RoleEnum, UserAuthMethod
from tests.selenium.conftest import app_instance
from tests.selenium.pages.home import HomePage


@pytest.fixture(autouse=True)
def setup_data(app_instance):
    with app_instance.app_context():
        admin = User(
            username='admin',
            email='admin@cineflow.me',
            password=generate_password_hash('Abc123@'),
            role=RoleEnum.ADMIN,
            full_name='Admin Test',
            is_active=True
        )
        db.session.add(admin)
        db.session.flush()

        admin_auth = UserAuthMethod(
            user_id=admin.id,
            provider="EMAIL",
            provider_id=admin.email,
        )
        db.session.add(admin_auth)
        db.session.commit()

        yield

        db.session.query(UserAuthMethod).filter_by(provider_id='admin@cineflow.me').delete()
        db.session.query(User).filter_by(email='admin@cineflow.me').delete()
        db.session.commit()


@pytest.mark.parametrize('email, password, is_success', [
    ('admin@cineflow.me', 'Abc123@', True),
    ('admin@cineflow.me', 'Abc123', False),
    ('admincineflow.me', 'Abc123@', False),
])
def test_login_email_flow(driver, local_server_url, email, password, is_success):
    home = HomePage(driver)
    home.host = local_server_url

    home.open_home()
    home.open_login_form()

    home.typing(By.NAME, "email", email)
    home.typing(By.NAME, "password", password)
    home.click(By.ID, "submit-login")

    alert_box_element = home.find(By.ID, "form_alert")
    box_classes = alert_box_element.get_attribute("class")

    if is_success:
        assert "bg-green-50" in box_classes
        time.sleep(1)
        assert home.is_on_correct_host()
    else:
        assert "bg-red-50" in box_classes
        auth_modal = home.find(By.ID, "auth")
        assert "hidden" not in auth_modal.get_attribute("class")

@pytest.mark.parametrize('signal, is_success', [
    ('GOOGLE_AUTH_SUCCESS', True),
    ('GOOGLE_AUTH_ERROR', False)
])
def test_login_google_flow(driver, local_server_url, signal, is_success):
    home = HomePage(driver)
    home.host = local_server_url

    home.open_home()
    home.open_login_form()

    home.click(*home.BTN_GOOGLE)
    time.sleep(2)

    simulate_google_js = f"""
        var event = new StorageEvent('storage', {{
            key: '{signal}',
            newValue: 'true'
        }});
        window.dispatchEvent(event);
    """
    driver.execute_script(simulate_google_js)
    alert_box_element = home.find(By.ID, "form_alert")
    box_classes = alert_box_element.get_attribute("class")
    if is_success:
        assert "bg-green-50" in box_classes
        auth_form = driver.find_element(By.ID, "auth")
        assert "hidden" in auth_form.get_attribute("class")
    else:
        assert "bg-red-50" in box_classes

def test_logout_flow(driver, local_server_url):
    home = HomePage(driver)
    home.host = local_server_url

    home.open_home()
    home.open_login_form()

    home.typing(By.NAME, "email", 'admin@cineflow.me')
    home.typing(By.NAME, "password", 'Abc123@')
    home.click(By.ID, "submit-login")

    alert_box_element = home.find(By.ID, "form_alert")
    box_classes = alert_box_element.get_attribute("class")

    assert "bg-green-50" in box_classes
    auth_form = driver.find_element(By.ID, "auth")
    assert "hidden" in auth_form.get_attribute("class")

    time.sleep(5)

    home.hover_avatar()
    home.click(*home.LOGOUT_BTN)

    # master_card = driver.find_element(*home.MASTER_CARD_NAV)
    # assert "Đăng nhập" in master_card.text

@pytest.mark.parametrize('username, full_name, email, otp, password, re_password, wait ,is_success', [
    ('test', 'Tran Test', 'test@cineflow.me', '123456', 'Abc123@', 'Abc123@', 1, True),
    ('test', 'Tran Test', 'test1@cineflow.me', '123456', 'Abc123@', 'Abc123@', 1, False),
    ('test1', 'Tran Test', 'test@cineflow.me', '123456', 'Abc123@', 'Abc123@', 1, False),
    ('test1', 'Tran Test', 'test1@cineflow.me', '123956', 'Abc123@', 'Abc123@', 1, False),
    ('test1', 'Tran Test', 'test1@cineflow.me', '123456', 'Abc123', 'Abc123', 1, False),
    ('test1', 'Tran Test', 'test1@cineflow.me', '123456', 'Abc123@', 'Abc1234@', 1, False),
])
def test_register_email_flow(app_instance, driver, local_server_url, username, full_name, email, otp, password, re_password,wait ,is_success):
    home = HomePage(driver)
    home.host = local_server_url

    home.open_home()
    home.open_login_form()
    home.open_regis_form()
    home.typing(*home.USERNAME_FIELD,username)
    home.typing(*home.FULLNAME_FIELD, full_name)
    home.typing(*home.EMAIL_FIELD, email)
    home.typing(*home.PASSWORD_FIELD, password)
    home.typing(*home.RE_PASSWORD_FIELD, re_password)
    home.click(*home.OTP_BTN)
    alert_box_element = home.find(By.ID, "form_alert")
    box_classes = alert_box_element.get_attribute("class")
    if "bg-red-50" in box_classes: return
    assert "bg-green-50" in box_classes
    with app_instance.app_context():
        cache.set(f"{email}", '123456')

    time.sleep(wait)
    home.typing(*home.OTP_FIELD, otp)
    home.click(*home.SUBMIT_BTN)
    alert_box_element = home.find(By.ID, "form_alert")
    box_classes = alert_box_element.get_attribute("class")
    if is_success:
        assert "bg-green-50" in box_classes
        time.sleep(1)
        assert home.is_on_correct_host()
        home.typing(By.NAME, "email", email)
        home.typing(By.NAME, "password", password)
        home.click(By.ID, "submit-login")

        alert_box_element = home.find(By.ID, "form_alert")
        box_classes = alert_box_element.get_attribute("class")

        if is_success:
            assert "bg-green-50" in box_classes
            time.sleep(1)
            assert home.is_on_correct_host()
        else:
            assert "bg-red-50" in box_classes
            auth_modal = home.find(By.ID, "auth")
            assert "hidden" not in auth_modal.get_attribute("class")
    else:
        assert "bg-red-50" in box_classes
        auth_modal = home.find(By.ID, "auth")
        assert "hidden" not in auth_modal.get_attribute("class")