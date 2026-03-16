from app import db


class User(db.Model):
    __tablename__ = 'users'
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(64), index=True, unique=True, nullable=False)
    password = db.Column(db.String(255), nullable=True)
    full_name = db.Column(db.String(100), nullable=True)
    phone_number = db.Column(db.String(20), nullable=True)
    email = db.Column(db.String(120), index=True, unique=True, nullable=False)
    avatar = db.Column(db.String(255), nullable=True)
    role = db.Column(db.String(20), default='user')
    is_active = db.Column(db.Boolean, default=True)
    auth_methods = db.relationship('UserAuthMethod', backref='user', lazy=True, cascade="all, delete-orphan")


class UserAuthMethod(db.Model):
    __tablename__ = 'user_auth_methods'
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    provider = db.Column(db.String(50), nullable=False)
    provider_id = db.Column(db.String(255), nullable=False)
    refresh_token = db.Column(db.String(500), nullable=True)