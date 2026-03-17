from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate

app = Flask(__name__, template_folder='templates', static_folder='static')
app.config.from_object('config')

db = SQLAlchemy(app)
migrate = Migrate(app, db)

from app import models
from .api import api
from .routes import routes
app.register_blueprint(api)
app.register_blueprint(routes)


