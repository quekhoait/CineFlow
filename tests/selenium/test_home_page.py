import random
import time
from datetime import date, datetime, timedelta
import pytest
from selenium.webdriver.common.by import By
from selenium.webdriver.support.wait import WebDriverWait
from werkzeug.security import generate_password_hash
from app import db, cache, models
from app.models import User, RoleEnum, UserAuthMethod
from tests.selenium.conftest import app_instance
from tests.selenium.pages.home import HomePage
from selenium.webdriver.support import expected_conditions as EC


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

        now_showing_films = [
            models.Film(title='Fantastic Four: First Steps', description='Gia đình siêu anh hùng đầu tiên của Marvel.',
                        genre='Action, Sci-Fi', age_limit=13, release_date=datetime.now() - timedelta(days=random.randint(0, 30)), expired_date=datetime.now() + timedelta(days=random.randint(30, 120)),
                        poster='https://encrypted-tbn3.gstatic.com/images?q=tbn:ANd9GcQd-BN3XSYs1IEmKerLM_hwcEKoJL25llBJmsAoWgTMXo3PHCCe',
                        duration=130),
            models.Film(title='Lật Mặt 8: Vòng Xoáy', description='Bom tấn hành động Lý Hải.', genre='Action, Drama',
                        age_limit=16, release_date=datetime.now() - timedelta(days=random.randint(0, 30)), expired_date=datetime.now() + timedelta(days=random.randint(30, 120)),
                        poster='https://cinema.momocdn.net/img/77210013985876184-lm81.png?size=M', duration=125),
            models.Film(title='Godzilla x Kong: The New Empire Sequel', description='Hai Titan huyền thoại tái hợp.',
                        genre='Action, Sci-Fi', age_limit=13,release_date=datetime.now() - timedelta(days=random.randint(0, 30)), expired_date=datetime.now() + timedelta(days=random.randint(30, 120)),
                        poster='https://encrypted-tbn0.gstatic.com/images?q=tbn:ANd9GcShQcL8k9ZNqTPP-vyiMwvfa8j6SF3bUc-thL0t4OBfO8ZDeg0d',
                        duration=115),
            models.Film(title='Fast X: Part 2', description='Chương cuối của gia đình Toretto.', genre='Action, Crime',
                        age_limit=16, release_date=datetime.now() - timedelta(days=random.randint(0, 30)), expired_date=datetime.now() + timedelta(days=random.randint(30, 120)),
                        poster='https://upload.wikimedia.org/wikipedia/vi/2/22/Fast_X_VN_poster.jpg', duration=140),
            models.Film(title='The Super Mario Bros. Movie 2', description='Hành trình mới của anh em Mario.',
                        genre='Animation, Adventure', age_limit=0, release_date=datetime.now() - timedelta(days=random.randint(0, 30)), expired_date=datetime.now() + timedelta(days=random.randint(30, 120)),
                        poster='https://encrypted-tbn2.gstatic.com/images?q=tbn:ANd9GcSbQAer_UacWJzfW1n8AREzPD6-MRfyAZT5aBEIhVYZqo0mclfO',
                        duration=100),
            models.Film(title='Five Nights at Freddy\'s 2', description='Cơn ác mộng kinh hoàng trở lại.',
                        genre='Horror, Thriller', age_limit=18, release_date=datetime.now() - timedelta(days=random.randint(0, 30)), expired_date=datetime.now() + timedelta(days=random.randint(30, 120)),
                        poster='https://cdn1.epicgames.com/spt-assets/5c65df08b03a43eb8be026116ef8e979/five-nights-at-freddys-into-the-pit-161gk.png',
                        duration=110),
            models.Film(title='Mortal Kombat 2', description='Giải đấu sinh tử bắt đầu.', genre='Action, Fantasy',
                        age_limit=18, release_date=date(2026, 4, 24), expired_date=date(2026, 6, 25),
                        poster='https://upload.wikimedia.org/wikipedia/en/thumb/9/9a/Mortal_Kombat_II_%28film%29_poster.jpg/250px-Mortal_Kombat_II_%28film%29_poster.jpg',
                        duration=120),
            models.Film(title='Kung Fu Panda 5', description='Gấu Po du hành vùng đất mới.', genre='Animation, Comedy',
                        age_limit=0, release_date=datetime.now() - timedelta(days=random.randint(0, 30)), expired_date=datetime.now() + timedelta(days=random.randint(30, 120)),
                        poster='https://cdn.moveek.com/storage/media/cache/tall/r6TxoNG69V.jpg', duration=95),
            models.Film(title='A Quiet Place: Day Two', description='Sống sót trong im lặng.', genre='Horror, Sci-Fi',
                        age_limit=16, release_date=datetime.now() - timedelta(days=random.randint(0, 30)), expired_date=datetime.now() + timedelta(days=random.randint(30, 120)),
                        poster='https://encrypted-tbn0.gstatic.com/images?q=tbn:ANd9GcQt7r7G9_OrP8w07k0rNVuvq-PSx47lUoV2VQ&s',
                        duration=105),
            models.Film(title='John Wick: Chapter 5', description='Sát thủ John Wick trở lại.',
                        genre='Action, Thriller',
                        age_limit=18,release_date=datetime.now() - timedelta(days=random.randint(0, 30)), expired_date=datetime.now() + timedelta(days=random.randint(30, 120)),
                        poster='https://encrypted-tbn0.gstatic.com/images?q=tbn:ANd9GcTYeBgUCM4wI8mP183zu9Me1cPLZbn8lpsBbQ&s',
                        duration=160)
        ]

        upcoming_films = [
            models.Film(title='The Mandalorian & Grogu', description='Star Wars hits the big screen.',
                        genre='Action, Sci-Fi',
                        age_limit=13, release_date=datetime.now() + timedelta(days=random.randint(0, 30)), expired_date=datetime.now() + timedelta(days=random.randint(30, 120)),
                        poster='https://m.media-amazon.com/images/M/MV5BYzVkMmJhNTgtNjYwOS00YjM0LThlNWEtNGExNmIxZjVkMmJhXkEyXkFqcGc@._V1_.jpg',
                        duration=125),
            models.Film(title='Jurassic World: Rebirth', description='A new era of dinosaurs begins.',
                        genre='Action, Sci-Fi',
                        age_limit=13, release_date=datetime.now() + timedelta(days=random.randint(0, 30)), expired_date=datetime.now() + timedelta(days=random.randint(30, 120)),
                        poster='https://m.media-amazon.com/images/M/MV5BNjg2NTcwYWQtYzk4NS00MTJhLWEzZjItMzIxNjk3YzlkYzU0XkEyXkFqcGc@._V1_FMjpg_UX1000_.jpg',
                        duration=135),
            models.Film(title='Shrek 5', description='The ogre and the donkey are back.', genre='Animation, Comedy',
                        age_limit=0,
                        release_date=datetime.now() + timedelta(days=random.randint(0, 30)), expired_date=datetime.now() + timedelta(days=random.randint(30, 120)),
                        poster='https://m.media-amazon.com/images/M/MV5BNmNkNmRkNDAtOTMzNC00MWYzLWJhNjMtYjNkZTNjODVhOTg2XkEyXkFqcGc@._V1_FMjpg_UX1000_.jpg',
                        duration=92),
            models.Film(title='Teenage Mutant Ninja Turtles 2', description='Turtles vs the Foot Clan.',
                        genre='Animation, Action', age_limit=13, release_date=datetime.now() + timedelta(days=random.randint(0, 30)), expired_date=datetime.now() + timedelta(days=random.randint(30, 120)),
                        poster='https://upload.wikimedia.org/wikipedia/en/6/6c/Teenage_Mutant_Ninja_Turtles_II_%281991_film%29_poster.jpg',
                        duration=102),
            models.Film(title='Tron: Ares', description='The digital world enters reality.', genre='Sci-Fi, Action',
                        age_limit=13,
                        release_date=datetime.now() + timedelta(days=random.randint(0, 30)),
                        expired_date=datetime.now() + timedelta(days=random.randint(30, 120)),
                        poster='https://lumiere-a.akamaihd.net/v1/images/p_disneymovies_tronares_poster_nowstreaming_1f6b491f.jpeg',
                        duration=120),
            models.Film(title='Frozen III', description='Elsa and Anna\'s new magical journey.',
                        genre='Animation, Family',
                        age_limit=0, release_date=datetime.now() + timedelta(days=random.randint(0, 30)), expired_date=datetime.now() + timedelta(days=random.randint(30, 120)),
                        poster='https://encrypted-tbn0.gstatic.com/images?q=tbn:ANd9GcQgsuZA9-Dp4oixpSLwrdRv0EV7ruI9MtFdZg&s',
                        duration=105),
            models.Film(title='The Hunger Games: Sunrise', description='The 50th Games story.', genre='Action, Drama',
                        age_limit=16, release_date=datetime.now() + timedelta(days=random.randint(0, 30)), expired_date=datetime.now() + timedelta(days=random.randint(30, 120)),
                        poster='https://upload.wikimedia.org/wikipedia/en/2/20/Sunrise_on_the_Reaping_book_cover.jpg',
                        duration=145),
            models.Film(title='Star Wars: New Jedi Order', description='Rey Skywalker builds the future.',
                        genre='Action, Sci-Fi', age_limit=13, release_date=datetime.now() + timedelta(days=random.randint(0, 30)), expired_date=datetime.now() + timedelta(days=random.randint(30, 120)),
                        poster='https://encrypted-tbn0.gstatic.com/images?q=tbn:ANd9GcRFXJzW4ZHKruTR_d2zTDQDk3JsB2PcPPOh1Q&s',
                        duration=150),
            models.Film(title='Lord of the Rings: Gollum', description='The journey to find the precious.',
                        genre='Fantasy, Adventure',
                        age_limit=13, release_date=datetime.now() + timedelta(days=random.randint(0, 30)), expired_date=datetime.now() + timedelta(days=random.randint(30, 120)),
                        poster='https://upload.wikimedia.org/wikipedia/en/thumb/2/23/The_Lord_of_the_Rings_Gollum.jpg/250px-The_Lord_of_the_Rings_Gollum.jpg',
                        duration=165),
            models.Film(title='Kraven the Hunter', description='Marvel\'s greatest hunter on the hunt.',
                        genre='Action, Sci-Fi',
                        age_limit=16, release_date=datetime.now() + timedelta(days=random.randint(0, 30)), expired_date=datetime.now() + timedelta(days=random.randint(30, 120)),
                        poster='https://upload.wikimedia.org/wikipedia/en/e/ec/Kraven_the_Hunter_%28film%29_poster.jpg',
                        duration=115)
        ]
        films_data = now_showing_films + upcoming_films
        db.session.add_all(films_data)
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

def test_load_list_films(driver, app_instance, local_server_url):
    home = HomePage(driver)
    home.host = local_server_url
    home.open_home()
    slider_1_element = home.find(*home.SLIDER_NOW_SHOWING)
    slider_2_element = home.find(*home.SLIDER_UPCOMING)

    now_showing_movies = driver.find_elements(*home.MOVIE_ITEMS_NOW_SHOWING)
    assert len(now_showing_movies) > 0

    up_showing_movies = driver.find_elements(*home.MOVIE_ITEMS_UPCOMING)
    assert len(up_showing_movies) > 0

    first_poster = now_showing_movies[0].find_element(By.TAG_NAME, "img")
    assert first_poster.get_attribute("src") != ""

    first_poster = up_showing_movies[0].find_element(By.TAG_NAME, "img")
    assert first_poster.get_attribute("src") != ""

    initial_scroll = driver.execute_script("return arguments[0].scrollLeft;", slider_1_element)
    assert initial_scroll == 0

    initial_scroll = driver.execute_script("return arguments[0].scrollLeft;", slider_2_element)
    assert initial_scroll == 0

    btn_right = home.find(*home.SCROLL_RIGHT_BTN_1)
    driver.execute_script("arguments[0].click();", btn_right)

    time.sleep(1)

    scrolled_right_pos = driver.execute_script("return arguments[0].scrollLeft;", slider_1_element)
    assert scrolled_right_pos > initial_scroll

    btn_left = home.find(*home.SCROLL_LEFT_BTN_1)
    driver.execute_script("arguments[0].click();", btn_left)

    time.sleep(1)

    scrolled_left_pos = driver.execute_script("return arguments[0].scrollLeft;", slider_1_element)
    assert scrolled_left_pos < scrolled_right_pos

    btn_right = home.find(*home.SCROLL_RIGHT_BTN_2)
    driver.execute_script("arguments[0].click();", btn_right)

    time.sleep(1)

    scrolled_right_pos = driver.execute_script("return arguments[0].scrollLeft;", slider_2_element)
    assert scrolled_right_pos > initial_scroll

    btn_left = home.find(*home.SCROLL_LEFT_BTN_2)
    driver.execute_script("arguments[0].click();", btn_left)

    time.sleep(1)

    scrolled_left_pos = driver.execute_script("return arguments[0].scrollLeft;", slider_2_element)
    assert scrolled_left_pos < scrolled_right_pos

    first_movie_detail_btn = now_showing_movies[0].find_element(By.CSS_SELECTOR, "div[onclick*='handleSelectFilm']")
    driver.execute_script("arguments[0].click();", first_movie_detail_btn)
    wait = WebDriverWait(driver, 10)
    wait.until(EC.url_contains("/film/detail"))
    assert "/film/detail" in driver.current_url
    current_id_in_session = driver.execute_script("return window.sessionStorage.getItem('currentId');")
    assert current_id_in_session is not None

def test_header_navigation(driver, app_instance, local_server_url):
    home = HomePage(driver)
    home.host = local_server_url
    wait = WebDriverWait(driver, 10)
    home.open_home()

    home.click(*home.NAV_SCHEDULE)
    wait.until(EC.url_contains("/schedule"))
    assert "/schedule" in driver.current_url

    home.click(*home.NAV_FILM)
    wait.until(EC.url_contains("/film"))
    assert "/film" in driver.current_url

    home.click(*home.NAV_HOME)
    wait.until(EC.url_contains("/"))
    assert "/" in driver.current_url

    home.open_login_form()
    home.typing(By.NAME, "email", 'admin@cineflow.me')
    home.typing(By.NAME, "password", 'Abc123@')
    home.click(By.ID, "submit-login")

    alert_box = wait.until(EC.visibility_of_element_located((By.ID, "form_alert")))
    wait.until(lambda d: "hidden" in alert_box.get_attribute("class"))
    time.sleep(1)

    home.hover_avatar()
    profile_btn = wait.until(EC.presence_of_element_located(home.PROFILE_BTN))
    driver.execute_script("arguments[0].click();", profile_btn)
    wait.until(EC.url_contains("/profile"))
    assert "/profile" in driver.current_url

    home.click(*home.NAV_HOME)
    wait.until(EC.url_contains("/"))
    assert "/" in driver.current_url

    home.hover_avatar()
    history_btn = wait.until(EC.presence_of_element_located(home.HISTORY_BTN))
    driver.execute_script("arguments[0].click();", history_btn)

    wait.until(EC.url_contains("/history"))
    assert "/history" in driver.current_url