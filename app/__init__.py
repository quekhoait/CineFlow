from flask import Flask
from flask_jwt_extended import JWTManager
from flask_sqlalchemy import SQLAlchemy
from flask_caching import Cache
from flask_mail import Mail
from authlib.integrations.flask_client import OAuth
import cloudinary
from config import config

db = SQLAlchemy()
mail = Mail()
cache = Cache()
jwt = JWTManager()
oauth = OAuth()
payment = None

def create_app(config_name):
    global payment
    app = Flask(__name__, template_folder='templates', static_folder='static')
    app.config.from_object(config[config_name])
    config[config_name].init_app(app)
    db.init_app(app)
    mail.init_app(app)
    cache.init_app(app)
    jwt.init_app(app)
    oauth.init_app(app)
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

    from .api import api
    from .routes import routes
    app.register_blueprint(api)
    app.register_blueprint(routes)

    from .admin import admin
    admin.init_app(app)

    return app