from app import db
from .base import BaseModel

class Cinema(BaseModel):
    __tablename__ = 'cinema'
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    name = db.Column(db.String(100), nullable=False)
    address = db.Column(db.String(255), nullable=False)
    province = db.Column(db.String(50))
    hotline = db.Column(db.String(20))

    rooms = db.relationship('Room', backref='cinema', lazy=True)

class Room(BaseModel):
    __tablename__ = 'room'
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    name = db.Column(db.String(50), nullable=False)
    row = db.Column(db.String(5))
    column = db.Column(db.Integer)
    cinema_id = db.Column(db.Integer, db.ForeignKey('cinema.id'), nullable=False)

    seats = db.relationship('Seat', backref='room', lazy=True)
    shows = db.relationship('Show', backref='room', lazy=True)

class Seat(BaseModel):
    __tablename__ = 'seat'
    code = db.Column(db.String(50), primary_key=True)
    type = db.Column(db.String(50))
    row = db.Column(db.String(5))
    column = db.Column(db.Integer)
    room_id = db.Column(db.Integer, db.ForeignKey('room.id'), nullable=False)

    tickets = db.relationship('Ticket', backref='seat', lazy=True)
