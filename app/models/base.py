from app import db
from sqlalchemy import func

class BaseModel(db.Model):
    __abstract__ = True
    created_at = db.Column(db.DateTime, serverdefault=func.now())
    updated_at = db.Column(db.DateTime, serverdefault=func.now(), serveronupdate=func.now())
