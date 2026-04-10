from sqlalchemy import func

from app.models import cinema
from app.models.cinema import Cinema, Room
from app.models.film import Film, Show
from datetime import datetime
from  app import db
from app.utils.errors import NotFoundError



def get_all():
    return Cinema.query.all()


def get_films_schedule_by_cinemaId(id, date):
    cinema = db.session.query(Cinema).filter(Cinema.id == id).first()
    if not cinema:
        raise NotFoundError(f"Cinema not found")
    time = date if date else datetime.now().date()
    results = db.session.query(Film, Show) \
        .join(Show, Film.id == Show.film_id) \
        .join(Room, Room.id == Show.room_id) \
        .filter(Room.cinema_id == id) \
        .filter(func.date(Show.start_time) == time) \
        .filter(Film.release_date <= time) \
        .filter(Film.expired_date >= time) \
        .order_by(Film.id, Show.start_time.asc()) \
        .all()
    films_dict = {}
    for film, show in results:
        if film.id not in films_dict:
            film.schedule = []
            films_dict[film.id] = film
        films_dict[film.id].schedule.append(show)
    return list(films_dict.values())

def get_by_id(id):
    return Cinema.query.filter(Cinema.id == id).first()

