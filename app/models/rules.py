from app import db
from .base import BaseModel

class Rules(BaseModel):
    __tablename__ = 'rules'
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    name = db.Column(db.String(100), nullable=False)
    type = db.Column(db.String(50))
    value = db.Column(db.String(50))
    active = db.Column(db.Boolean, default=True)

    user_id= db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)