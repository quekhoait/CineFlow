from alembic.autogenerate.compare import server_defaults

from app import db
from sqlalchemy import func

class BaseModel(db.Model):
    __abstract__ = True
    created_at = db.Column(db.DateTime, server_default=func.now())
    updated_at = db.Column(db.DateTime, server_default=func.now(), onupdate=func.now())
