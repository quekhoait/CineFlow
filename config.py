from datetime import timedelta

JWT_SECRET_KEY = 'CINEMAFLOW'
JWT_ACCESS_TOKEN_EXPIRES = timedelta(days=7)
JWT_REFRESH_TOKEN_EXPIRES = timedelta(days=30)
