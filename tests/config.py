TESTING = True
DEBUG = False
SQLALCHEMY_DATABASE_URI = "sqlite:///:memory:"
SQLALCHEMY_TRACK_MODIFICATIONS = False
WTF_CSRF_ENABLED = False
PAGE_SIZE = 2

# Đảm bảo các key bắt buộc vẫn có giá trị (hoặc dummy data)
# SECRET_KEY = "test_secret"
# GOOGLE_CLIENT_ID = "test_id"
# GOOGLE_CLIENT_SECRET = "test_secret"
# GOOGLE_SERVER_METADATA_URL = "https://test.com"
# GOOGLE_CLIENT_SCOPE = "openid email profile"