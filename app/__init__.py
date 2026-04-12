from flask import Flask
from flask_admin import Admin
from flask_jwt_extended import JWTManager
from flask_sqlalchemy import SQLAlchemy
from flask_caching import Cache
from flask_mail import Mail
from authlib.integrations.flask_client import OAuth
import cloudinary

from .utils.seed import seed_data

app = Flask(__name__, template_folder='templates', static_folder='static')
app.config.from_object('config')

db = SQLAlchemy(app)
from app.models import *
with app.app_context():
    db.create_all()
cache = Cache(app)
jwt = JWTManager(app)
mail = Mail(app)
oauth = OAuth(app)
oauth.register(
    name='google',
    client_id=app.config['GOOGLE_CLIENT_ID'],
    client_secret=app.config['GOOGLE_CLIENT_SECRET'],
    server_metadata_url=app.config['GOOGLE_SERVER_METADATA_URL'],
    client_kwargs={'scope': app.config['GOOGLE_CLIENT_SCOPE']},
)

cloudinary.config(
    cloud_name=app.config['CLOUDINARY_CLOUD_NAME'],
    api_key=app.config['CLOUDINARY_API_KEY'],
    api_secret=app.config['CLOUDINARY_API_SECRET'],
)

from .pattern.method_payment import PaymentContext
payment = PaymentContext(app.config)

if app.config['SEED'] == True:
    seed_data(app, db)

from .api import api
from .routes import routes
from .admin import admin
app.register_blueprint(api)
app.register_blueprint(routes)
admin.init_app(app)


