from app import Show, Ticket
from app.utils.errors import NotFoundError


def get_show_seats(show_id:int):
    show = Show.query.filter_by(id=show_id).first()
    if not show:
        raise NotFoundError("Show not found")
    booked_tickets = Ticket.query.filter_by(show_id=show_id, active=True).all()
    booked_seat_codes = [ticket.seat_code for ticket in booked_tickets]

    seats_data = []
    for seat in show.room.seats:
        seats_data.append({
            "code": seat.code,
            "row": seat.row,
            "col": seat.column,
            "type": seat.type.value,
            "is_booked": seat.code in booked_seat_codes
        })

    return {
        "show_info": {
            "film_title": show.film.title,
            "cinema_name": show.room.cinema.name,
            "poster": show.film.poster,
            "room_name": show.room.name,
            "start_time": show.start_time.strftime("%Hh%M' %d/%m/%Y")
        },
        "seats": seats_data
    }