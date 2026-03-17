from app.models.film import Film
from app import db
class FilmRepo:
    @staticmethod
    def create(data):
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
        db.session.commit()
        return new_film

    def update(id, data):
        film = Film.query.filter_by(id=id).first()
        for key, value in data.items():
            setattr(film, key, value)
        db.session.commit()
        return film

    def get_all(self):
        film = Film.query.all()
        return film

    def get(id):
        film = Film.query.filter_by(id=id).first()
        if not film:
            return None
        return film
