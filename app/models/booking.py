from enum import Enum
from datetime import datetime
from app import db
from .base import BaseModel

class BookingStatus(Enum):
    CANCELED = 'CANCELED'
    BOOKED = 'BOOKED'

class BookingPaymentStatus(Enum):
    PENDING = 'PENDING'
    PAID = 'PAID'
    REFUNDING = 'REFUNDING'
    REFUNDED = 'REFUNDED'

class PaymentStatus(Enum):
    PENDING = 'PENDING'
    SUCCESS = 'SUCCESS'
    FAILED = 'FAILED'

class PaymentType(Enum):
    PAYMENT = 'PAYMENT'
    REFUND = 'REFUND'

class Booking(BaseModel):
    __tablename__ = 'booking'
    code = db.Column(db.String(8), primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    total_price = db.Column(db.Float, nullable=False)
    status = db.Column(db.Enum(BookingStatus), default=BookingStatus.BOOKED, nullable=False)
    payment_status = db.Column(db.Enum(BookingPaymentStatus), default=BookingPaymentStatus.PENDING, nullable=False)
    express_time = db.Column(db.DateTime)
    check_in = db.Column(db.DateTime)

    tickets = db.relationship('Ticket', backref='booking', lazy=True)
    payments = db.relationship('Payment', backref='booking', lazy=True)

class Ticket(BaseModel):
    __tablename__ = 'ticket'
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    show_id = db.Column(db.Integer, db.ForeignKey('show.id'), nullable=False)
    seat_code = db.Column(db.String(50), db.ForeignKey('seat.code'), nullable=False)
    booking_code = db.Column(db.String(8), db.ForeignKey('booking.code'), nullable=False)
    price = db.Column(db.Float)
    active = db.Column(db.Boolean, default=True)

class Payment(BaseModel):
    __tablename__ = 'payment'
    code = db.Column(db.String(12), primary_key=True)
    booking_code = db.Column(db.String(8), db.ForeignKey('booking.code'), nullable=False)
    payment_method = db.Column(db.String(50))
    transaction_id = db.Column(db.String(100))
    amount = db.Column(db.Float, nullable=False)
    pay_url = db.Column(db.Text)
    expired_time = db.Column(db.DateTime)
    status = db.Column(db.Enum(PaymentStatus), default=PaymentStatus.PENDING, nullable=False)
    type = db.Column(db.Enum(PaymentType), default=PaymentType.PAYMENT, nullable=False)