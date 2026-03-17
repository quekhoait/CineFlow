from app import db

class Cinema(db.Model):
    __tablename__ = 'cinema'
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    name = db.Column(db.String(100), nullable=False)
    address = db.Column(db.String(255), nullable=False)
    province = db.Column(db.String(50))
    hotline = db.Column(db.String(20))

    rooms = db.relationship('Room', backref='cinema', lazy=True)

class Room(db.Model):
    __tablename__ = 'room'
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    name = db.Column(db.String(50), nullable=False)
    capacity = db.Column(db.Integer, nullable=False)
    cinema_id = db.Column(db.Integer, db.ForeignKey('cinema.id'), nullable=False)

    seats = db.relationship('Seat', backref='room', lazy=True)
    shows = db.relationship('Show', backref='room', lazy=True)

class Seat(db.Model):
    __tablename__ = 'seat'
    code = db.Column(db.String(50), primary_key=True)
    type = db.Column(db.String(50))
    row = db.Column(db.String(5))
    column = db.Column(db.Integer)
    room_id = db.Column(db.Integer, db.ForeignKey('room.id'), nullable=False)

    show_seats = db.relationship('ShowSeat', backref='seat', lazy=True)
