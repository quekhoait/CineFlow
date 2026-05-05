import os
from datetime import timedelta

from dotenv import load_dotenv

dotenv_path = os.path.join(os.path.dirname(__file__), '.env')
if os.path.exists(dotenv_path):
    load_dotenv(dotenv_path)

def get_env_bool(name, default=False):
    val = os.environ.get(name)
    if val is None:
        return default
    return str(val).lower() in ('true', '1', 't', 'yes', 'y')


class Config:
    ACCESS_KEY = os.environ.get('ACCESS_KEY', '0cb87b9870d7a23f02dece7648ad')
    SECRET_KEY = os.environ.get('SECRET_KEY', '1ee5da987f2df0cb87b9870d7a23f02dece7648ad518cf9a43')

    DB_USER = os.environ.get('DB_USER', 'root')
    DB_PASSWORD = os.environ.get('DB_PASSWORD', 'root')
    DB_HOST = os.environ.get('DB_HOST', 'localhost')
    DB_PORT = os.environ.get('DB_PORT', '3306')
    DB_NAME = os.environ.get('DB_NAME', 'cineflow')
    DB_URI_TEMPLATE = f"mysql+pymysql://{DB_USER}:{DB_PASSWORD}@{DB_HOST}:{DB_PORT}/{DB_NAME}?charset=utf8mb4"

    # Cache
    CACHE_TYPE = 'SimpleCache'
    CACHE_DEFAULT_TIMEOUT = os.environ.get('CACHE_DEFAULT_TIMEOUT', 300)

    # Mail
    SENDGRID_API_KEY = os.environ.get("SENDGRID_API_KEY")
    SENDGRID_FROM = os.environ.get("SENDGRID_FROM")

    # Google
    GOOGLE_CLIENT_ID = os.environ.get("GOOGLE_CLIENT_ID")
    GOOGLE_CLIENT_SECRET = os.environ.get("GOOGLE_CLIENT_SECRET")
    GOOGLE_SERVER_METADATA_URL = 'https://accounts.google.com/.well-known/openid-configuration'
    GOOGLE_CLIENT_SCOPE = 'https://www.googleapis.com/auth/userinfo.email https://www.googleapis.com/auth/userinfo.profile'

    # JWT
    JWT_TOKEN_LOCATION = ['cookies']
    JWT_SECRET_KEY = os.environ.get("JWT_SECRET_KEY")
    JWT_ACCESS_TOKEN_EXPIRES = timedelta(hours=1)
    JWT_REFRESH_TOKEN_EXPIRES = timedelta(days=30)
    JWT_COOKIE_CSRF_PROTECT = False

    # PAYMENT
    ## MOMO
    MOMO_PARTNER_CODE = os.environ.get("MOMO_PARTNER_CODE")
    MOMO_ACCESS_KEY = os.environ.get("MOMO_ACCESS_KEY")
    MOMO_SECRET_KEY = os.environ.get("MOMO_SECRET_KEY")
    MOMO_CREATE_ENDPOINT = "https://test-payment.momo.vn/v2/gateway/api/create"
    MOMO_REFUND_ENDPOINT = "https://test-payment.momo.vn/v2/gateway/api/refund"
    MOMO_RETURN_URL = os.environ.get("MOMO_RETURN_URL")
    MOMO_IPN_URL = os.environ.get("MOMO_IPN_URL")
    MOMO_EXPIRE_AFTER = 15

    # CLOUDINARY
    CLOUDINARY_CLOUD_NAME = os.environ.get("CLOUDINARY_CLOUD_NAME")
    CLOUDINARY_API_KEY = os.environ.get("CLOUDINARY_API_KEY")
    CLOUDINARY_API_SECRET = os.environ.get("CLOUDINARY_API_SECRET")

    @staticmethod
    def init_app(app):
        pass


class DevelopmentConfig(Config):
    DEBUG = True
    SQLALCHEMY_DATABASE_URI = os.environ.get('DEV_DATABASE_URI') or Config.DB_URI_TEMPLATE
    # SQLALCHEMY_ECHO = True


class TestingConfig(Config):
    TESTING = True
    SQLALCHEMY_DATABASE_URI = os.environ.get('TEST_DATABASE_URI') or 'sqlite:///'
    WTF_CSRF_ENABLED = False
    SERVER_NAME = 'localhost:5000'


class ProductionConfig(Config):
    SQLALCHEMY_DATABASE_URI = os.environ.get('DATABASE_URL') or Config.DB_URI_TEMPLATE
    SESSION_COOKIE_SECURE = True
    SESSION_COOKIE_SAMESITE = 'Lax'
    SESSION_COOKIE_HTTPONLY = True
    SESSION_TYPE = 'filesystem'

    @classmethod
    def init_app(cls, app):
        Config.init_app(app)

        import logging
        from logging.handlers import RotatingFileHandler

        if not os.path.exists('logs'):
            os.mkdir('logs')

        file_handler = RotatingFileHandler('logs/cineflow.log', maxBytes=10240000, backupCount=10)
        file_formatter = logging.Formatter(
            '%(asctime)s | %(levelname)s | %(message)s | [in %(pathname)s:%(lineno)d]'
        )
        file_handler.setFormatter(file_formatter)
        file_handler.setLevel(logging.INFO)
        app.logger.addHandler(file_handler)
        app.logger.setLevel(logging.INFO)
        app.logger.info('Start with cineflow')

config = {
    'development': DevelopmentConfig,
    'testing': TestingConfig,
    'production': ProductionConfig,
    'default': DevelopmentConfig
}