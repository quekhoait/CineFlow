from app.dto.film_dto import FilmResponse
from tests.conftest import client, sample_films
import pytest

@pytest.mark.parametrize("strategy, expected_count", [
    (None, 10),
    ("showing", 4),
    ("future", 3)
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
    print(response.data)
    data = response.get_json()
    assert response.status_code == 400
    assert data['message'] == "Missing title film"
    assert data['data'] == ""






