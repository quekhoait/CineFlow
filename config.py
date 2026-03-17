from datetime import timedelta

DB_NAME = 'cineflow'
DB_USER = 'root'
DB_PASSWORD = 'root'
DB_HOST = 'localhost'
DB_PORT = 3306

SECRET_KEY = '1ee5da987f2df0cb87b9870d7a23f02dece7648ad518cf9a43'

# Database
SQLALCHEMY_DATABASE_URI = f"mysql+pymysql://{DB_USER}:{DB_PASSWORD}@{DB_HOST}:{DB_PORT}/{DB_NAME}?charset=utf8mb4"

CACHE_TYPE = 'SimpleCache'
CACHE_DEFAULT_TIMEOUT = 300

# Mail Config
MAIL_SERVER = "smtp.gmail.com"
MAIL_PORT = 587
MAIL_USE_TLS = True
MAIL_USERNAME = "mailbox.together@gmail.com"
MAIL_PASSWORD = "iiyh hglt rivy dscj"
MAIL_DEFAULT_SENDER = f"CineFlowo Support <{MAIL_USERNAME}>"

#GOOGLE
GOOGLE_CLIENT_ID = "959971118501-l6a373amphjccsm96bangb27bu4d7ie4.apps.googleusercontent.com"
GOOGLE_CLIENT_SECRET = "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"
GOOGLE_SERVER_METADATA_URL='https://accounts.google.com/.well-known/openid-configuration'
GOOGLE_CLIENT_SCOPE='https://www.googleapis.com/auth/userinfo.email https://www.googleapis.com/auth/userinfo.profile'

# JWT Config
JWT_SECRET_KEY = '1ee5da987f2df0cb87b9870d7a23e500218c7d6b4ff02dece7648ad518cf9a43'
JWT_ACCESS_TOKEN_EXPIRES = timedelta(days=7)
JWT_REFRESH_TOKEN_EXPIRES = timedelta(days=30)
