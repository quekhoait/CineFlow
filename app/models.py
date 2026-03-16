from app import db
class Film(db.Model):
    __tablename__="films"
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(255))
    description = db.Column(db.Text)
    genre=db.Column(db.String(100))
    age_limit = db.Column(db.Integer)
    release_date = db.Column(db.Date)
    expired_date = db.Colmn(db.Date)
    duration = db.Column(db.Integer)

    def to_dict(self):
        return {
            "id": self.id,
            "title": self.title,
            "description": self.description,
            "genre": self.genre,
            "age_limit": self.age_limit,
            "release_date": self.release_date,
            "expired_date": self.expired_date,
            "duration": self.duration,

        }