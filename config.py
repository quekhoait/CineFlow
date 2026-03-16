from datetime import timedelta

DB_NAME = 'cineflow'
DB_USER = 'root'
DB_PASSWORD = 'root'
DB_HOST = 'localhost'
DB_PORT = 3306

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

# JWT Config
JWT_SECRET_KEY = "1ee5da987f2df0cb87b9870d7a23e500218c7d6b4ff02dece7648ad518cf9a43"
JWT_ACCESS_TOKEN_EXPIRES = timedelta(days=7)
JWT_REFRESH_TOKEN_EXPIRES = timedelta(days=30)
