from enum import Enum
from app import db
from .base import BaseModel

class RoleEnum(Enum):
    ADMIN = 'admin'
    USER = 'user'

class User(BaseModel):
    __tablename__ = 'user'
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    username = db.Column(db.String(50), unique=True, nullable=False)
    password = db.Column(db.String(255), nullable=False)
    full_name = db.Column(db.String(100))
    phone_number = db.Column(db.String(15))
    email = db.Column(db.String(50), unique=True)
    avatar = db.Column(db.String(255))
    role = db.Column(db.Enum(RoleEnum), default=RoleEnum.USER)
    is_active = db.Column(db.Boolean, default=True)

    auth_methods = db.relationship('UserAuthMethod', backref='user', lazy=True)
    bookings = db.relationship('Booking', backref='user', lazy=True)
    rules = db.relationship('Rules', backref='user', lazy=True)

class UserAuthMethod(BaseModel):
    __tablename__ = 'user_auth_method'
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    provider = db.Column(db.String(50))
    provider_id = db.Column(db.String(100))
    refresh_token = db.Column(db.String(255))
