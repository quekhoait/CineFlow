
DEBUG = False
from datetime import timedelta
from dotenv import load_dotenv
import os
load_dotenv()

ACCESS_KEY = os.getenv('ACCESS_KEY')
SECRET_KEY = os.getenv('SECRET_KEY')

DB_USER = os.getenv('DB_USER')
DB_PASSWORD = os.getenv('DB_PASSWORD')
DB_HOST = os.getenv('DB_HOST')
DB_PORT = os.getenv('DB_PORT')
DB_NAME = os.getenv('DB_NAME')

# Mail
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

# JWT
JWT_SECRET_KEY = os.getenv("JWT_SECRET_KEY")
JWT_ACCESS_TOKEN_EXPIRES = timedelta(days=7)
JWT_REFRESH_TOKEN_EXPIRES = timedelta(days=30)

# PAYMENT
# MOMO
MOMO_PARTNER_CODE = os.getenv("MOMO_PARTNER_CODE")
MOMO_ACCESS_KEY = os.getenv("MOMO_ACCESS_KEY")
MOMO_SECRET_KEY = os.getenv("MOMO_SECRET_KEY")
MOMO_CREATE_ENDPOINT = "https://test-payment.momo.vn/v2/gateway/api/create"
MOMO_REFUND_ENDPOINT = "https://test-payment.momo.vn/v2/gateway/api/refund"
MOMO_RETURN_URL = "https://leechlike-unlethal-talisha.ngrok-free.dev/"
MOMO_IPN_URL = "https://leechlike-unlethal-talisha.ngrok-free.dev/api/payments/momo/callback"
MOMO_EXPIRE_AFTER= 15