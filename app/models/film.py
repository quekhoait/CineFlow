from app import db
class Film(db.Model):
    __tablename__ = "film"
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(255))
    description = db.Column(db.Text)
    genre = db.Column(db.String(100))
    age_limit = db.Column(db.Integer)
    release_date = db.Column(db.Date)
    expired_date = db.Column(db.Date)
    duration = db.Column(db.Integer)
