class APIError(Exception):
    def __init__(self, message: str, status_code: int):
        super().__init__()
        self.message = message
        self.status_code = status_code

class InvalidInput(APIError):
    def __init__(self, message: str = "Invalid input"):
        super().__init__(message, status_code=400)

class UserLoginFailed(APIError):
    def __init__(self, message: str = "Email or password are wrong"):
        super().__init__(message, status_code=401)

class UnauthorizedError(APIError):
    def __init__(self, message: str = "Unauthorized"):
        super().__init__(message, status_code=401)
        
class ExistingUserError(APIError):
    def __init__(self, message: str = "Email already exists"):
        super().__init__(message, status_code=409)
        
class SendEmailFailed(APIError):
    def __init__(self, message: str = "Send email failed"):
        super().__init__(message, status_code=500)
        
class SendNotificationFailed(APIError):
    def __init__(self, message: str = "Send notification failed"):
        super().__init__(message, status_code=500)

class InvalidOtpError(APIError):
    def __init__(self, message: str = "Invalid OTP"):
        super().__init__(message, status_code=400)

class RegisterFailed(APIError):
    def __init__(self, message: str = "Register failed"):
        super().__init__(message, status_code=500)

class FilmNotFound(APIError):
    def __init__(self, message="Film not found."):
        super().__init__(message, status_code=404)

class InvalidDuration(APIError):
    def __init__(self, message="Duration must be greater than 0."):
        super().__init__(message, status_code=400)

class InvalidDateRange(APIError):
    def __init__(self, message="Release date must be before expired date."):
        super().__init__(message, status_code=400)

class NotFoundError(APIError):
    def __init__(self, message: str = "Not found"):
        super().__init__(message, status_code=404)
        
class ExpiredError(APIError):
    def __init__(self, message: str = "Expired ...."):
        super().__init__(message, status_code=400)

class TicketCanceledError(APIError):
    def __init__(self, message: str = "Ticket canceled"):
        super().__init__(message, status_code=400)

<<<<<<< HEAD
class NoPaymentsError(APIError):
    def __init__(self, message: str = "You don't have any payments"):
        super().__init__(message, status_code=400)

class RefundedPaymentsError(APIError):
    def __init__(self, message: str = "Refunded payments"):
        super().__init__(message, status_code=409)
=======
class TicketExistError(APIError):
    def __init__(self, message: str = "Ticket already exists"):
        super().__init__(message, status_code=409)

>>>>>>> main
