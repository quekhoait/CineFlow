from enum import Enum
from app import db
from .base import BaseModel

class TicketStatus(Enum):
    AVAILABLE = 'AVAILABLE'
    HOLD = 'HOLD'
    BOOKED = 'BOOKED'

class Film(db.Model):
    __tablename__ = 'film'
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    title = db.Column(db.String(100), nullable=False)
    description = db.Column(db.Text)
    genre = db.Column(db.String(100))
    age_limit = db.Column(db.Integer)
    release_date = db.Column(db.Date)
    expired_date = db.Column(db.Date)
    poster = db.Column(db.String(500), nullable=False)
    duration = db.Column(db.Integer)
    shows = db.relationship('Show', backref='film', lazy=True)

class Show(BaseModel):
    __tablename__ = 'show'
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    start_time = db.Column(db.DateTime, nullable=False)
    film_id = db.Column(db.Integer, db.ForeignKey('film.id'), nullable=False)
    room_id = db.Column(db.Integer, db.ForeignKey('room.id'), nullable=False)

    tickets = db.relationship('Ticket', backref='show', lazy=True)