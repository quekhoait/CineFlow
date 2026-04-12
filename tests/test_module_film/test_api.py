from datetime import date, timedelta
from unittest.mock import patch

from app import Show
from app.dto.film_dto import FilmResponse
from app.utils.errors import NotFoundError
from tests.conftest import client, sample_films, sample_shows, sample_cinema_system, mock_jwt
import pytest

@pytest.mark.parametrize("strategy, expected_count", [
    (None, 7),
    ('all', 7),
    ("showing", 4),
    ("future", 3),
    ("111222", 7)
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
#
def test_search_film_no_title(client, sample_films):
    response = client.get('/api/films/search')
    data = response.get_json()
    assert response.status_code == 200
    assert len(data['data']) == 7

def test_get_schedule_by_film(client, sample_films, sample_cinema_system, sample_shows):
    response = client.get('/api/films/1/cinemas')
    data = response.get_json()
    assert response.status_code == 200
    assert len(data['data']) == 1

@patch('app.services.film_service.list')
def test_film_api_internal_error(mock_service, client):
    mock_service.side_effect = Exception("Database disconnected")
    response = client.get('/api/films')
    assert response.status_code == 500
    assert response.json['status'] == "error"
    assert response.json['message'] == "Internal Server Error"
    assert "Database disconnected" in response.json['data']

@patch('app.services.film_service.get_by_id')
def test_list_film_api_internal_error(mock_service, client):
    mock_service.side_effect = Exception("Database disconnected")
    response = client.get('/api/films/1')
    assert response.status_code == 500
    assert response.json['status'] == "error"
    assert response.json['message'] == "Internal Server Error"
    assert "Database disconnected" in response.json['data']

@patch('app.services.film_service.get_by_title')
def test_search_film_api_internal_error(mock_service, client):
    mock_service.side_effect = Exception("Database disconnected")
    response = client.get('/api/films/search?title=Lật')
    assert response.status_code == 500
    assert response.json['status'] == "error"
    assert response.json['message'] == "Internal Server Error"
    assert "Database disconnected" in response.json['data']

@patch('app.services.film_service.get_schedule_by_film_and_date')
def test_get_cinemas_internal_error(mock_service, client):
    mock_service.side_effect = Exception("Database disconnected")
    response = client.get('/api/films/1/cinemas')
    assert response.status_code == 500
    assert response.json['status'] == "error"
    assert response.json['message'] == "Internal Server Error"
    assert "Database disconnected" in response.json['data']

@patch('app.services.film_service.get_schedule_by_film_and_date')
def test_cinemas_api_not_found_error(mock_service, client):
    mock_service.side_effect = NotFoundError("Cinema not found")
    response = client.get('/api/films/99/cinemas?date=2026-04-12')
    assert response.status_code == 404
    assert response.json['status'] == "error"
    assert response.json['message'] == "Cinema not found"

#
# ##############################################
def test_get_all_cinema(client, sample_cinema_system):
    response = client.get('/api/cinemas')
    data = response.get_json()
    actual_data = data.get('data', [])
    c = sum(len(item['location']) for item in actual_data)
    assert response.status_code == 200
    assert c == 3

@patch('app.services.cinema_service.list')
def test_list_cinema_api_internal_error(mock_service, client):
    mock_service.side_effect = Exception("Database disconnected")
    response = client.get('/api/cinemas')
    assert response.status_code == 500
    assert response.json['status'] == "error"
    assert response.json['message'] == "Internal Server Error"
    assert "Database disconnected" in response.json['data']

#
def test_get_cinema_by_id_success(client, sample_cinema_system):
    response = client.get('/api/cinemas/1')
    data = response.get_json()
    assert response.status_code == 200
    assert data['data']['id'] == 1
    assert data['data']['name'] == 'CGV Vincom'
    assert data['status'] == "success"

def test_get_schedule_film_by_cinema_success(client, sample_cinema_system, sample_films, sample_shows):
    response = client.get('/api/cinemas/1/films')
    data = response.get_json()
    assert response.status_code == 200
    assert len(data['data']) == 2

def test_get_cinema_by_id_error(client, sample_cinema_system):
    response = client.get('/api/cinemas/99')
    assert response.status_code == 404

def test_get_cinema_by_date_error(client, sample_cinema_system):
    response = client.get('/api/cinemas/1/films?date=2026-ab-12')
    assert response.status_code == 400

@patch('app.services.cinema_service.get_films_schedule_by_cinemaId')
def test_get_film_api_internal_error(mock_service, client):
    mock_service.side_effect = Exception("Database disconnected")
    response = client.get('/api/cinemas/1/films')
    assert response.status_code == 500
    assert response.json['status'] == "error"
    assert response.json['message'] == "Internal Server Error"
    assert "Database disconnected" in response.json['data']

@patch('app.services.cinema_service.get_by_id')
def test_get_cinema_internal_error(mock_service, client):
    mock_service.side_effect = Exception("Database disconnected")
    response = client.get('/api/cinemas/1')
    assert response.status_code == 500
    assert response.json['status'] == "error"
    assert response.json['message'] == "Internal Server Error"
    assert "Database disconnected" in response.json['data']



# ###
# # Show
@pytest.mark.parametrize("show_id, expected_status, count_seat", [
    (1, 200, 1),
    (999, 404, None),
    ("abc", 404, None)
])
def test_get_seats_by_show_api(client, mock_jwt, sample_shows, sample_rules, show_id, expected_status, count_seat):
    response = client.get(f'/api/shows/{show_id}')
    assert response.status_code == expected_status
    if expected_status == 200:
        data = response.get_json()
        assert len(data['data']['seats']) == count_seat

@patch('app.services.show_service.get_show_seats_info')
def test_get_seat_internal_error( mock_service,mock_jwt, client):
    mock_service.side_effect = Exception("Database disconnected")
    response = client.get('/api/shows/1')
    assert response.status_code == 500
    assert response.json['status'] == "error"
    assert response.json['message'] == "Have a problem while getting show seats info"
    assert "Database disconnected" in response.json['data']







