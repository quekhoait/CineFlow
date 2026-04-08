from marshmallow import fields

from app import SeatType
from app.dto.cinema_dto import CinemaResponse
from app.dto.user_dto import UserResponse
from app.models.booking import BookingStatus, PaymentStatus, BookingPaymentStatus
from app.dto import BaseSchema

class BookingRequest(BaseSchema):
    id_show = fields.Integer(required=True, error_messages={'required': 'Show ID is required'})
    code_seats = fields.List(fields.String(), required=True, error_messages={'required': 'Seat codes is required'})

class BookingSchema(BaseSchema):
    code = fields.String(required=True, error_messages={'required': 'Booking code is required'})
    user_id = fields.Integer(required=True, error_messages={'required': 'User id is required'})
    total_price = fields.Float(required=True, error_messages={'required': 'Total price is required'})

class SeatResponse(BaseSchema):
    seat_code = fields.String()
    price = fields.Float()
    seat_type = fields.Enum(enum=SeatType)
    type = fields.Method("format_seat_type")
    name = fields.Method("format_seat_label")
    def format_seat_label(self, obj):
        if obj.seat.row and obj.seat.column:
            return f"{obj.seat.row}{obj.seat.column}"
        return None

    def format_seat_type(self, obj):
        return obj.seat.type.value


class BookingDetailResponse(BaseSchema):
    code = fields.String()
    film_title = fields.Method("get_film_title")
    poster = fields.Method("get_poster")
    cinema_name = fields.Method("get_cinema_name")
    address = fields.Method("get_address")
    room_name = fields.Method("get_room_name")
    start_time = fields.Method("get_start_time")
    payment_status = fields.Enum(enum=BookingPaymentStatus)
    total_price = fields.Float()
    seats = fields.Nested(SeatResponse, attribute="tickets", many=True)

    def get_film_title(self, obj):
        return obj.tickets[0].show.film.title

    def get_cinema_name(self, obj):
        return obj.tickets[0].show.room.cinema.name

    def get_address(self, obj):
        return obj.tickets[0].show.room.cinema.address

    def get_poster(self, obj):
        return obj.tickets[0].show.film.poster

    def get_room_name(self, obj):
        return obj.tickets[0].show.room.name

    def get_start_time(self, obj):
        return obj.tickets[0].show.start_time.strftime("%Hh%M' %d/%m/%Y")

class BookingResponse(BaseSchema):
    code = fields.String()
    total_price = fields.Float()
    status = fields.Enum(enum=BookingStatus)
    payment_status = fields.Enum(enum=BookingPaymentStatus)
    start_time = fields.DateTime()
    film_title = fields.String()
    created_at = fields.DateTime()
    updated_at = fields.DateTime()

class CancelRequest(BaseSchema):
    code = fields.String(required=True, error_messages={"required": "Please provide code!!"})

class SeatBookedResponse(BaseSchema):
    booking_code = fields.String()
    seat = fields.Nested(SeatResponse)

class BookingsResponse(BaseSchema):
    code = fields.String()
    payment_status = fields.Enum(enum=BookingPaymentStatus)
    film_title = fields.Method("get_film_title")
    start_time = fields.Method("get_start_time")

    def get_film_title(self, obj):
        if not obj.tickets:
            return "N/A"
        return obj.tickets[0].show.film.title

    def get_start_time(self, obj):
        if not obj.tickets:
            return "N/A"
        return obj.tickets[0].show.start_time.strftime("%Hh%M' %d/%m/%Y")

class BookingsPageResponse(BaseSchema):
    page = fields.Integer()
    total = fields.Integer()
    limit = fields.Integer(attribute="per_page")
    isNext = fields.Boolean(attribute="has_next")
    isPrevious = fields.Boolean(attribute="has_prev")
    bookings = fields.Nested(BookingsResponse, many=True, attribute="items")