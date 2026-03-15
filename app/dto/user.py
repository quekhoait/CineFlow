from pydantic import EmailStr, BaseModel, Field


class UserRequest(BaseModel):
    email: EmailStr
    password: str = Field(
        ...,
        min_length=6,
        max_length=32,
        pattern=r"^(?=.*[a-z])(?=.*[A-Z])(?=.*\d)(?=.*[@$!%*?&])[A-Za-z\d@$!%*?&]{6,}$",
    )

    def object_to_model(self):
        pass

class UserResponse(BaseModel):
    username: str
    full_name: str
    phone_number: str
    email: str
    avatar: str
    is_active: bool
    access_token: str
    refresh_token: str

    def model_to_object(self):
        pass
