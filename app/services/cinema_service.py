from datetime import datetime

from app.dto.cinema_dto import CinemaResponse, CinemaFilmResponse, CinemaProvince
from app.dto.film_dto import FilmResponse
from app.repository import cinema_repo
from app.utils.errors import NotFoundError, IdError, InvalidDateError, APIError


def list() -> CinemaProvince:
    try:
        cinemas = cinema_repo.get_all()
        grouped = {}
        for c in cinemas:
            if c.province not in grouped:
                grouped[c.province] = []
            grouped[c.province].append({"id":c.id,"name": c.name, "address": c.address})
        res = [
            {"province": p, "location": l} 
            for p, l in grouped.items()
        ]
        return CinemaProvince(many=True).dump(res)
    except Exception as e:
        raise Exception(str(e))

def get_films_schedule_by_cinemaId(id, date) -> CinemaFilmResponse:
    if id is None:
        raise IdError("ID is required")
    if not isinstance(id, int):
        raise IdError("ID must be a number")
    if id <= 0:
        raise IdError("ID must be a positive integer")
    if date is not None:
        try:
            datetime.strptime(str(date), '%Y-%m-%d')
        except (APIError, ValueError, TypeError):
            raise InvalidDateError()
    film = cinema_repo.get_films_schedule_by_cinemaId(id, date)
    return CinemaFilmResponse(many=True).dump(film)

def get_by_id(id)-> CinemaResponse:
    if id is None:
        raise IdError("ID is required")
    if not isinstance(id, int):
        raise IdError("ID must be a number")
    if id <= 0:
        raise IdError("ID must be a positive integer")
    cinema = cinema_repo.get_by_id(id)
    if not cinema:
        raise NotFoundError("cinema not found")
    return CinemaResponse().dump(cinema)

