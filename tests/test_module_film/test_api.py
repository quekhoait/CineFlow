from datetime import date, timedelta

from app.dto.film_dto import FilmResponse
from tests.conftest import client, sample_films, sample_shows, sample_cinema_system
import pytest

@pytest.mark.parametrize("strategy, expected_count", [
    (None, 10),
    ('all', 10),
    ("showing", 4),
    ("future", 3),
    ("111222", 10)
])
def test_get_films_by_strategy(client, sample_films, strategy, expected_count):
    response = client.get(f'/api/films?strategy={strategy}')
    data = response.get_json()
    assert response.status_code == 200
    assert len(data['data']) == expected_count



def test_get_film_by_id_success(client, sample_films):
    response = client.get('/api/films/1')
    data = response.get_json()
    film = data['data']
    assert response.status_code == 200
    assert film['title'] == "Lật Mặt 8: Kẻ Vô Diện"

def test_get_film_by_id_not_found(client, sample_films):
    response = client.get('/api/films/9999')
    data = response.get_json()
    assert response.status_code == 404
    assert data['status'] == "error"

def test_search_films_success(client, sample_films):
    response = client.get('/api/films/search?title=Lật')
    data = response.get_json()
    films = data['data']

    assert response.status_code == 200
    assert len(films) == 1

    expected_film = next(f for f in films if f['title'] == 'Lật Mặt 8: Kẻ Vô Diện')
    assert films[0]['title'] == expected_film['title']

def test_search_films_error(client, sample_films):
    response = client.get('/api/films/search?title=Khoa')
    data = response.get_json()
    films = data['data']
    assert response.status_code == 404
    assert len(films) == 0

def test_search_film_no_title(client, sample_films):
    response = client.get('/api/films/search')
    data = response.get_json()
    assert response.status_code == 400
    assert data['message'] == "Missing title film"
    assert data['data'] == ""


##############################################
def test_get_all_cinema(client, sample_cinema_system):
    response = client.get('/api/cinemas')
    data = response.get_json()
    actual_data = data.get('data', [])
    c = sum(len(item['location']) for item in actual_data)
    assert response.status_code == 200
    assert c == 3

def test_get_cinema_by_id_success(client, sample_cinema_system):
    response = client.get('/api/cinemas/1')
    data = response.get_json()
    assert response.status_code == 200
    assert data['data']['id'] == 1
    assert data['data']['name'] == 'CGV Vincom'
    assert data['status'] == "success"

def test_get_cinema_by_id_error(client, sample_cinema_system):
    response = client.get('/api/cinemas/99')
    assert response.status_code == 404

#lấy suât chiếu quả rap 1 chưa chọn ngày
@pytest.mark.parametrize("test_date, expected_count", [
    (None, 1),
    (date.today().isoformat(), 1),
    ((date.today() + timedelta(days=1)).isoformat(), 1),
    ((date.today() + timedelta(days=10)).isoformat(), 0),
])
def test_get_show_film_by_cinema_and_date(client, sample_films, sample_cinema_system, sample_shows, test_date,
                                          expected_count):
    url = '/api/cinemas/1/films'
    if test_date:
        url += f'?date={test_date}'
    response = client.get(url)
    assert response.status_code == 200
    data = response.get_json()
    actual_data = data.get('data', [])
    total_shows = sum(len(film['schedule']) for film in actual_data)
    assert total_shows == expected_count

#test film lấy suất chieeu chưa chiếu trong ngày


#







