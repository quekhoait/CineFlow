from app import db
from app.dto.film_dto import CreateFilm, GetFilm
from app.repository.film_repo import FilmRepo
from flask import request


class FilmServices:
    @staticmethod
    def create(data):
        schema =CreateFilm()
        res = schema.load(data) #load dữ lieuj json lên
        film = FilmRepo.create(res)
        s = GetFilm()
        return s.dump(film)

    @staticmethod
    def update(id):
        data = request.get_json()
        schema = CreateFilm(partial=True)
        res = schema.load(data)
        film = FilmRepo.update(id, res)
        s = GetFilm()
        return s.dump(film)

    @staticmethod
    def list():
        films = FilmRepo.get_all()
        schema = GetFilm(many=True)
        return schema.dump(films) #convert thừ object vè json

    @staticmethod
    def get_by_id(id):
        films = FilmRepo.get(id)
        schema = GetFilm()
        return schema.dump(films)



