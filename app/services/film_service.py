from app import db
from app.dto.film_dto import CreateFilm, FilmResponse, FilmResponseBase
from app.models.film import Film
from app.pattern.strategy_films import FilmFilterContext
from app.repository import film_repo
from flask import request
from app.utils .errors import FilmNotFound, InvalidDuration, InvalidDateRange
from app.pattern import strategy_films


def update(data: CreateFilm, id) -> FilmResponse:
    film= film_repo.get_by_id(id)
    release = datetime.fromisoformat(data["release_date"])
    expired = datetime.fromisoformat(data["expired_date"])
    if not film:
        raise FilmNotFound()
    if "duration" in data and data["duration"] <= 0:
        raise InvalidDuration()
    if release and expired:
        if release > expired:
            raise InvalidDateRange()
    try:
        updated_film = film_repo.update(id, data)
        db.session.commit()
        return FilmResponse().dump(updated_film)
    except Exception as e:
        db.session.rollback()
        raise Exception((str(e)))

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
    film = film_repo.get_by_id(id)
    if not film:
        raise FilmNotFound()
    return FilmResponse().dump(film)

def get_by_title(data) -> FilmResponse:
    films = film_repo.get_by_title(data)
    if not films:
        raise FilmNotFound()
    return FilmResponse(many=True).dump(films)

