from app import db
from app.dto.film_dto import CreateFilm, FilmResponse, FilmResponseBase
from app.models.film import Film
from app.repository import film_repo
from flask import request

def create(data: CreateFilm) -> FilmResponse:
    if data.get("duration") <= 0:
        raise ValueError("Duration must be greater than 0")
    if data.get("release_date") > data.get("expired_date"):
        raise ValueError("Release date must be before expired date")
    try:
        film = film_repo.create(data)
        return FilmResponse().dump(film)
    except Exception as e:
        raise Exception((str(e)))

def update(data: CreateFilm, id) -> FilmResponse:
    film= film_repo.get_by_id(id)
    if not film:
        raise ValueError("Film not found")
    if "duration" in data and data["duration"] <= 0:
        raise ValueError("Duration must be greater than 0")
    if "release_date" in data and "expired_date" in data:
        if data["release_date"] > data["expired_date"]:
            raise ValueError("Release date must be before expired date")
    try:
        updated_film = film_repo.update(id, data)
        return FilmResponse().dump(updated_film)
    except Exception as e:
        raise Exception((str(e)))

def list() -> FilmResponse:
    try:
        films = film_repo.get_all()
        return FilmResponse(many=True).dump(films) #convert thừ object vè json
    except Exception as e:
        raise Exception(str(e))

def get_by_id(id) -> FilmResponse:
    film = film_repo.get_by_id(id)
    if not film:
        raise  ValueError("Film not found")
    return FilmResponse().dump(film)

def get_by_title(data) -> FilmResponse:
    films = film_repo.get_by_title(data)
    if not films:
        raise ValueError("Film not found")
    return FilmResponse(many=True).dump(films)

def get_now_showing() -> FilmResponseBase:
    films = film_repo.get_now_showing()
    if not films:
        raise ValueError("Film not found")
    return FilmResponseBase(many=True).dump(films)

def get_release_showing() -> FilmResponseBase:
    films = film_repo.get_release_showing()
    if not films:
        raise ValueError("Film not found")
    return FilmResponseBase(many=True).dump(films)

