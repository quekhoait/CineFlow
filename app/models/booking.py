from enum import Enum
from datetime import datetime
from app import db
from .base import BaseModel

class BookingStatus(Enum):
    PENDING = 'PENDING'
    CANCELED = 'CANCELED'
    PAID = 'PAID'


class PaymentStatus(Enum):
    PENDING = 'PENDING'
    SUCCESSFUL = 'SUCCESSFUL'
    FAILED = 'FAILED',
    REFUNDED = 'REFUNDED'

class Booking(BaseModel):
    __tablename__ = 'booking'
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    total_price = db.Column(db.Float, nullable=False)
    status = db.Column(db.Enum(BookingStatus), default=BookingStatus.PENDING, nullable=False)

    tickets = db.relationship('Ticket', backref='booking', lazy=True)
    payments = db.relationship('Payment', backref='booking', lazy=True)

class Ticket(BaseModel):
        __tablename__ = 'ticket'
        id = db.Column(db.Integer, primary_key=True, autoincrement=True)
        booking_id = db.Column(db.Integer, db.ForeignKey('booking.id'), nullable=False)
        show_seat_id = db.Column(db.Integer, db.ForeignKey('show_seat.id'), nullable=False)
        qr_code = db.Column(db.String(100))

class Payment(BaseModel):
        __tablename__ = 'payment'
        id = db.Column(db.Integer, primary_key=True, autoincrement=True)
        booking_id = db.Column(db.Integer, db.ForeignKey('booking.id'), nullable=False)
        payment_method = db.Column(db.String(50))
        transaction_id = db.Column(db.String(100))
        momo_trans_id = db.Column(db.String(100))
        amount = db.Column(db.Float, nullable=False)
        pay_url = db.Column(db.Text)
        expired_time = db.Column(db.DateTime)
        status = db.Column(db.Enum(PaymentStatus), default=PaymentStatus.PENDING, nullable=False)

