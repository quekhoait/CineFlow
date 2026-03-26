from flask import Flask
from flask_jwt_extended import JWTManager
from flask_sqlalchemy import SQLAlchemy
from flask_caching import Cache
from flask_mail import Mail
from authlib.integrations.flask_client import OAuth
from config import configs  # Import dictionary configs từ config.py

db = SQLAlchemy()
cache = Cache()
jwt = JWTManager()
mail = Mail()
oauth = OAuth()


def create_app(config_class):
    app = Flask(__name__, template_folder='templates', static_folder='static')

    app.config.from_object(config_class)

    # Gắn các extension vào app
    db.init_app(app)
    cache.init_app(app)
    jwt.init_app(app)
    mail.init_app(app)
    oauth.init_app(app)

    oauth.register(
        name='google',
        client_id=app.config.get('GOOGLE_CLIENT_ID'),
        client_secret=app.config.get('GOOGLE_CLIENT_SECRET'),
        server_metadata_url=app.config.get('GOOGLE_SERVER_METADATA_URL'),
        client_kwargs={'scope': app.config.get('GOOGLE_CLIENT_SCOPE')},
    )

    # Import và đăng ký Blueprint bên trong hàm để tránh Circular Import
    from .api import api
    from .routes import routes
    app.register_blueprint(api)
    app.register_blueprint(routes)

    return app