from enum import Enum
from datetime import datetime
from app import db

class BookingStatus(Enum):
    PENDING = 'PENDING'
    CANCELED = 'CANCELED'
    PAID = 'PAID'

class PaymentStatus(Enum):
    PENDING = 'PENDING'
    SUCCESSFUL = 'SUCCESSFUL'
    FAILED = 'FAILED'

class Booking(db.Model):
    __tablename__ = 'booking'
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    total_price = db.Column(db.Float, nullable=False)
    status = db.Column(db.Enum(BookingStatus), default=BookingStatus.PENDING, nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.now(), nullable=False)

    tickets = db.relationship('Ticket', backref='booking', lazy=True)
    payments = db.relationship('Payment', backref='booking', lazy=True)

class Ticket(db.Model):
        __tablename__ = 'ticket'
        id = db.Column(db.Integer, primary_key=True, autoincrement=True)
        booking_id = db.Column(db.Integer, db.ForeignKey('booking.id'), nullable=False)
        show_seat_id = db.Column(db.Integer, db.ForeignKey('show_seat.id'), nullable=False)
        qr_code = db.Column(db.String(100))

class Payment(db.Model):
        __tablename__ = 'payment'
        id = db.Column(db.Integer, primary_key=True, autoincrement=True)
        booking_id = db.Column(db.Integer, db.ForeignKey('booking.id'), nullable=False)
        payment_method = db.Column(db.String(50))
        transaction_id = db.Column(db.String(100))
        amount = db.Column(db.Float, nullable=False)
        pay_url = db.Column(db.Text)
        expired_time = db.Column(db.DateTime)
        status = db.Column(db.Enum(PaymentStatus), default=PaymentStatus.PENDING, nullable=False)