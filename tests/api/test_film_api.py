import pytest
from app.utils.errors import FilmNotFound

def test_get_film_success(client, mocker):
    mock_film = {
        "id": 1,
        "title": "Test Film",
        "genre": "Action",
        "duration": 120,
        "description": "An action-packed film",
        "age_limit": 13,
        "poster": "poster.jpg"
    }
    mocker.patch(
        "app.services.film_service.get_by_id",
        return_value=mock_film
    )
    response = client.get("/api/films/1")
    data = response.get_json()
    assert response.status_code == 200
    assert data["status"] == "success"
    assert data["message"] == "get film success"
    assert data["data"]["title"] == "Test Film"
    assert data["data"]["genre"] == "Action"
    assert data["data"]["duration"] == 120


def test_get_film_not_found(client, mocker):
    mocker.patch(
        "app.services.film_service.get_by_id",
        side_effect=FilmNotFound()
    )
    response = client.get("/api/films/999")
    assert response.status_code == 404