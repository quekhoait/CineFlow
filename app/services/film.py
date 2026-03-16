from app import db
class FilmServices:
    @staticmethod
    def create_film(data):
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
        return new_film.to_dict()

    @staticmethod
    def update_film(id, data):
        film = Film.query.filter_by(id=id).first()
        if not film:
            return None
        film = Film(
            title = data.get("title"),
            description = data.get("description"),
            genre = data.get("genre"),
            age_limit = data.get("age_limit"),
            release_date = data.get("release_date"),
            expired_date = data.get("expired_date"),
            duration = data.get("duration")
        )
        db.session.add(film)
        db.session.commit()
        return film.to_dict()

    @staticmethod
    def get_all_film():
        films=Film.query.all()
        for film in films:
            return film.to_dict()

    @staticmethod
    def get_film_by_id(id):
        film = Film.query.filter_by(id=id).first()
        if not film:
            return None
        return film.to_dict()


