from sqlalchemy import func

from app.models.cinema import Cinema, Room
from app.models.film import Film, Show
from datetime import datetime


from  app import db
def get_all():
    return Cinema.query.all()

def get_films_schedule_by_cinemaId(id, date):
    time = datetime.now().date()
    if date:
        time = date
    films = db.session.query(Film).join(Show).join(Room).filter(Room.cinema_id == id).filter(func.date(Show.start_time)==time).filter(Film.release_date <= time, Film.expired_date >= time).distinct().all()
    for film in films:
        schedule = db.session.query(Show).join(Room).filter(Show.film_id == film.id).filter(Room.cinema_id == id).filter(func.date(Show.start_time)==time).order_by(Show.start_time.asc()).all()
        film.schedule = schedule
    return films

def get_by_id(id):
    return Cinema.query.filter_by(id=id).first()

