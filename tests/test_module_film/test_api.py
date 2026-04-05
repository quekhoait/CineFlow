from app.dto.film_dto import FilmResponse
from tests.conftest import client, sample_films


def test_get_films(client, sample_films):
    response = client.get('/api/films?strategy=all')
    data = response.get_json()
    assert len(data['data']) == 10


def test_get_films_now_showing(client, sample_films):
    response = client.get('/api/films?strategy=showing')
    data = response.get_json()
    assert len(data['data']) == 4

def test_get_films_now_future(client, sample_films):
    response = client.get('/api/films?strategy=future')
    data = response.get_json()
    assert len(data['data']) == 3

def test_get_film_by_id(client, sample_films):
    response = client.get('/api/films/1')
    data = response.get_json()
    film = data['data']
    assert response.status_code == 200
    assert film['title'] == "Lật Mặt 8: Kẻ Vô Diện"