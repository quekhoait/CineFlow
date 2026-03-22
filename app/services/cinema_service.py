from app.dto.cinema_dto import CinemaResponse, CinemaFilmResponse, CinemaProvince
from app.dto.film_dto import FilmResponse
from app.repository import cinema_repo

# def list() -> CinemaResponse:
#     try:
#         cinemas = cinema_repo.get_all()
#         return CinemaResponse(many=True).dump(cinemas)
#     except Exception as e:
#         raise Exception(str(e))

def list() -> CinemaProvince:
    try:
        cinemas = cinema_repo.get_all()
        grouped = {}
        for c in cinemas:
            if c.province not in grouped:
                grouped[c.province] = []
            grouped[c.province].append({"name": c.name, "address": c.address})
        res = [{"province": p, "location": l} for p, l in grouped.items()]
        return CinemaProvince(many=True).dump(res)
    except Exception as e:
        raise Exception(str(e))

def get_films_schedule_by_cinemaId(id, date) -> CinemaFilmResponse:
    film = cinema_repo.get_films_schedule_by_cinemaId(id, date)
    return CinemaFilmResponse(many=True).dump(film)


