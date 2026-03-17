from datetime import timedelta

DB_NAME = 'cineflow'
DB_USER = 'root'
DB_PASSWORD = "123456"
DB_HOST = 'localhost'
DB_PORT = 3306

SQLALCHEMY_DATABASE_URI = f"mysql+pymysql://{DB_USER}:{DB_PASSWORD}@{DB_HOST}:{DB_PORT}/{DB_NAME}?charset=utf8mb4"

CACHE_TYPE = 'SimpleCache'
CACHE_DEFAULT_TIMEOUT = 300

JWT_SECRET_KEY = "CINEMAFLOW"
JWT_ACCESS_TOKEN_EXPIRES = timedelta(days=7)
JWT_REFRESH_TOKEN_EXPIRES = timedelta(days=30)
