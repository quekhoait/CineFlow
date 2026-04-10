from app.models.film import Film
from datetime import datetime
from app import db, Show, Room, Cinema
from sqlalchemy import func

def update(id, data):
    film = Film.query.filter_by(id=id).first()
    for key, value in data.items():
        setattr(film, key, value)
    return film

def get_all() :
    return Film.query.all()


def get_by_id(id) :
    film = Film.query.filter_by(id=id).first()
    return film

def get_by_title(data):
    return Film.query.filter(Film.title.ilike(f"%{data}%")).all()

def get_now_showing():
    now = datetime.now()
    return Film.query.filter(Film.release_date <= now, Film.expired_date >= now).all()

def get_release_showing():
    now = datetime.now()
    return Film.query.filter(Film.release_date > now).all()


def get_schedule_by_film_and_date(film_id, date):
    film = db.session.query(Film).filter(Film.id == film_id).first()
    if not film:
        raise NotFoundError(f"Film not found")
    time = date if date else datetime.now().date()
    results = db.session.query(Show, Room, Cinema) \
        .join(Room, Show.room_id == Room.id) \
        .join(Cinema, Room.cinema_id == Cinema.id) \
        .filter(Show.film_id == film_id) \
        .filter(func.date(Show.start_time) == time) \
        .order_by(Cinema.id, Show.start_time.asc()) \
        .all()
    cinemas_dict = {}
    for show, room, cinema in results:
        if cinema.id not in cinemas_dict:
            cinema.schedule = []
            cinemas_dict[cinema.id] = cinema
        show.room_name = room.name
        cinemas_dict[cinema.id].schedule.append(show)

    return list(cinemas_dict.values())