class APIError(Exception):
    def __init__(self, message: str, status_code: int):
        super().__init__()
        self.message = message
        self.status_code = status_code

class InvalidInput(APIError):
    def __init__(self, message: str = "Invalid input"):
        super().__init__(message, status_code=400)

class UserLoginEmailFailed(APIError):
    def __init__(self, message: str = "Email or password are wrong"):
        super().__init__(message, status_code=400)

class UserLoginGoogleFailed(APIError):
    def __init__(self, message: str = "Google login failed"):
        super().__init__(message, status_code=400)

class UnauthorizedError(APIError):
    def __init__(self, message: str = "Unauthorized"):
        super().__init__(message, status_code=401)
        
class ExistingUserError(APIError):
    def __init__(self, message: str = "Email already exists"):
        super().__init__(message, status_code=409)

class ExistingUsernameError(APIError):
    def __init__(self, message: str = "Username already exists"):
        super().__init__(message, status_code=409)

class SendEmailFailed(APIError):
    def __init__(self, message: str = "Send email failed"):
        super().__init__(message, status_code=500)
        
class SendNotificationFailed(APIError):
    def __init__(self, message: str = "Send notification failed"):
        super().__init__(message, status_code=500)

class InvalidOtpError(APIError):
    def __init__(self, message: str = "Incorrect OTP verification code"):
        super().__init__(message, status_code=400)

class ExpiredOtpError(APIError):
    def __init__(self, message: str = "OTP has expired"):
        super().__init__(message, status_code=400)

class RegisterFailed(APIError):
    def __init__(self, message: str = "Register failed"):
        super().__init__(message, status_code=500)

class NotFoundError(APIError):
    def __init__(self, message="Film not found."):
        super().__init__(message, status_code=404)

class TransactionComplete(APIError):
    def __init__(self, message: str = "Transaction completed"):
        super().__init__(message, status_code=400)

class InvalidDateError(APIError):
    def __init__(self, message="Date invalid"):
        super().__init__(message, status_code=400)


class InvalidDuration(APIError):
    def __init__(self, message="Duration must be greater than 0."):
        super().__init__(message, status_code=400)

class InvalidDateRange(APIError):
    def __init__(self, message="Release date must be before expired date."):
        super().__init__(message, status_code=400)

class NotFoundError(APIError):
    def __init__(self, message: str = "Not found"):
        super().__init__(message, status_code=404)


class MissingTitleFilm(APIError):
    def __init__(self, message="Missing title film"):
        super().__init__(message, status_code=400)


class ExpiredError(APIError):
    def __init__(self, message: str = "Expired ...."):
        super().__init__(message, status_code=400)

class ExpiredTicketError(APIError):
    def __init__(self, message: str = "You are only allowed to perform any operations at least 2 hours before the show starts!"):
        super().__init__(message, status_code=400)

class TicketCanceledError(APIError):
    def __init__(self, message: str = "Ticket canceled"):
        super().__init__(message, status_code=400)

class CancelCheckedInTicketError(APIError):
    def __init__(self, message: str = "Ticket checked in"):
        super().__init__(message, status_code=400)

class NoPaymentsError(APIError):
    def __init__(self, message: str = "You don't have any payments"):
        super().__init__(message, status_code=400)

class NoPaymentsMethod(APIError):
    def __init__(self, message: str = "Payments method not found"):
        super().__init__(message, status_code=404)

class RefundedPaymentsError(APIError):
    def __init__(self, message: str = "Refunded payments"):
        super().__init__(message, status_code=409)

class PaymentsError(APIError):
    def __init__(self, message: str = "Payment error"):
        super().__init__(message, status_code=409)


class TicketExistError(APIError):
    def __init__(self, message: str = "Ticket already exists"):
        super().__init__(message, status_code=409)

class LimitBookingError(APIError):
    def __init__(self, message: str = "Maximum seats quantity"):
        super().__init__(message, status_code=409)

class IdError(APIError):
    def __init__(self, message: str = "error id..."):
        super().__init__(message, status_code=400)