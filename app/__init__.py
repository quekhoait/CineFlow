from flask import Flask
from flask_jwt_extended import JWTManager


from flask_sqlalchemy import SQLAlchemy
db = SQLAlchemy()


app = Flask(__name__, template_folder='templates', static_folder='static')
app.config.from_object('config')

db.init_app(app)
# db = SQLAlchemy(app)
jwt = JWTManager(app)

from .api import api
from .routes import routes
app.register_blueprint(api)
app.register_blueprint(routes)

