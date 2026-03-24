from app.models.film import Film
from app import db
from datetime import datetime

def create(data) :
    new_film = Film(
        title = data.get("title"),
        description = data.get("description"),
        genre = data.get("genre"),
        age_limit = data.get("age_limit"),
        release_date = data.get("release_date"),
        expired_date = data.get("expired_date"),
        duration =data.get("duration")
    )
    db.session.add(new_film)
    db.session.flush()
    return new_film

def update(id, data):
    film = Film.query.filter_by(id=id).first()
    for key, value in data.items():
        setattr(film, key, value)
    db.session.commit()
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