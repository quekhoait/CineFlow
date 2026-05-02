from app import db
from app.dto.film_dto import FilmRequest, FilmResponse, FilmResponseBase, FilmCinemaResponse
from app.models.film import Film
from app.pattern.strategy_films import FilmFilterContext
from app.repository import film_repo
from flask import request, jsonify
from app.utils.errors import InvalidDuration, InvalidDateRange, MissingTitleFilm, IdError, NotFoundError, \
    InvalidDateError, APIError
from app.pattern import strategy_films
from datetime import datetime



def list(query=None) -> FilmResponse:
    try:
        context = FilmFilterContext()
        films = context.get_films(query)
        if query in ["future", "showing"]:
            return FilmResponseBase(many=True).dump(films)
        return FilmResponse(many=True).dump(films)
    except Exception as e:
        raise Exception(str(e))

def get_by_id(id) -> FilmResponse:
    if id is None:
        raise IdError("ID is required")
    if not isinstance(id, int):
        raise IdError("ID must be a number")
    if id <= 0:
        raise IdError("ID must be a positive integer")
    film = film_repo.get_by_id(id)
    if not film:
        raise NotFoundError("Film not found")
    return FilmResponse().dump(film)

def get_by_title(title) -> FilmResponse:
    if not title or not title.strip():
        films = film_repo.get_all()
    else:
        films = film_repo.get_by_title(title.strip())
    if not films:
        raise NotFoundError("Film not found")
    return FilmResponseBase(many=True).dump(films)

def get_schedule_by_film_and_date(id, date) -> FilmCinemaResponse:
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
    cinemas = film_repo.get_schedule_by_film_and_date(id, date)
    return FilmCinemaResponse(many=True).dump(cinemas)