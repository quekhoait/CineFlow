
from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask_caching import Cache

app = Flask(__name__, template_folder='templates', static_folder='static')
app.config.from_object('config')
db = SQLAlchemy()
cache = Cache()

db.init_app(app)
cache.init_app(app)
from .api import api
from .routes import routes
app.register_blueprint(api)
app.register_blueprint(routes)
with app.app_context():
    db.create_all()

