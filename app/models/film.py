from enum import Enum
from app import db
from .base import BaseModel


class ShowSeatStatus(Enum):
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
    poster = db.Column(db.String(100), nullable=False)
    duration = db.Column(db.Integer)
    shows = db.relationship('Show', backref='film', lazy=True)

class Show(BaseModel):
    __tablename__ = 'show'
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    start_time = db.Column(db.DateTime, nullable=False)
    film_id = db.Column(db.Integer, db.ForeignKey('film.id'), nullable=False)
    room_id = db.Column(db.Integer, db.ForeignKey('room.id'), nullable=False)

    show_seats = db.relationship('ShowSeat', backref='show', lazy=True)

class ShowSeat(BaseModel):
    __tablename__ = 'show_seat'
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    show_id = db.Column(db.Integer, db.ForeignKey('show.id'), nullable=False)
    seat_code = db.Column(db.String(50), db.ForeignKey('seat.code'), nullable=False)
    status = db.Column(db.Enum(ShowSeatStatus), default=ShowSeatStatus.AVAILABLE)

    tickets = db.relationship('Ticket', backref='show_seat', lazy=True)


