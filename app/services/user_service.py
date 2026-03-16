import random
from app import cache
from app.dto.user_dto import RegisterRequest
from app.repository import user_repo
from app.utils.errors import ExistingEmailError


def send_otp(data):
    email = data.email
    if user_repo.get_user_id_by_email(email):
        raise ExistingEmailError()

    otp = str(random.randint(100000, 999999))
    cache.set(f"{email}", otp)

    

def register(request: RegisterRequest):
    pass


