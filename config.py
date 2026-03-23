from datetime import timedelta
from dotenv import load_dotenv
import os
load_dotenv()

DB_USER = os.getenv('DB_USER')
DB_PASSWORD = os.getenv('DB_PASSWORD')
DB_HOST = os.getenv('DB_HOST')
DB_PORT = os.getenv('DB_PORT')
DB_NAME = os.getenv('DB_NAME')




# Database
SQLALCHEMY_DATABASE_URI = f"mysql+pymysql://{DB_USER}:{DB_PASSWORD}@{DB_HOST}:{DB_PORT}/{DB_NAME}?charset=utf8mb4"

# Cache
CACHE_TYPE = 'SimpleCache'
CACHE_DEFAULT_TIMEOUT = 300

# Mail Config
MAIL_SERVER = "smtp.gmail.com"
MAIL_PORT = 587
MAIL_USE_TLS = True
MAIL_PASSWORD = os.getenv("MAIL_PASSWORD")
MAIL_USERNAME = os.getenv('MAIL_USERNAME')
MAIL_DEFAULT_SENDER = f"CineFlowo Support <{MAIL_USERNAME}>"

# GOOGLE
GOOGLE_CLIENT_ID = os.getenv("GOOGLE_CLIENT_ID")
GOOGLE_CLIENT_SECRET = os.getenv("GOOGLE_CLIENT_SECRET")
GOOGLE_SERVER_METADATA_URL='https://accounts.google.com/.well-known/openid-configuration'
GOOGLE_CLIENT_SCOPE='https://www.googleapis.com/auth/userinfo.email https://www.googleapis.com/auth/userinfo.profile'

# JWT Config
JWT_SECRET_KEY = os.getenv("JWT_SECRET_KEY")
JWT_ACCESS_TOKEN_EXPIRES = timedelta(days=7)
JWT_REFRESH_TOKEN_EXPIRES = timedelta(days=30)
