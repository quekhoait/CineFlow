from app.services import film_service
import pytest

from app.utils.errors import FilmNotFound
from tests.conftest import client, sample_films


def test_service_get_by_title_success(sample_films):
    result = film_service.get_by_title("Lật")
    assert result[0]['title'] == "Lật Mặt 8: Kẻ Vô Diện"

def test_service_get_by_title_error(sample_films):
    with pytest.raises(FilmNotFound):
        result = film_service.get_by_title("Khoa")

def test_service_get_by_id_success(sample_films):
    result = film_service.get_by_id(1)
    assert result['title'] == "Lật Mặt 8: Kẻ Vô Diện"

def test_service_get_by_id_error(sample_films):
    with pytest.raises(FilmNotFound):
        film_service.get_by_id(9999)

@pytest.mark.parametrize("strategy, expected_type", [
    ("future", list),
    ("showing", list),
    (None, list)
])
def test_service_list_strategies(sample_films, strategy, expected_type):
    result = film_service.list(strategy)
    assert isinstance(result, expected_type)

