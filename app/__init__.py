from flask import Flask
from flask_jwt_extended import JWTManager
from flask_sqlalchemy import SQLAlchemy
from flask_caching import Cache
from flask_mail import Mail

app = Flask(__name__, template_folder='templates', static_folder='static')
app.config.from_object('config')

db = SQLAlchemy(app)
# from app.models import *
# with app.app_context():
#     db.create_all()
cache = Cache(app)
jwt = JWTManager(app)
mail = Mail(app)

from .api import api
from .routes import routes
app.register_blueprint(api)
app.register_blueprint(routes)

