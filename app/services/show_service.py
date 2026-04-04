from app.repository import show_repo
from app.utils.errors import NotFoundError


def get_show_seats_info(show_id):
    show = show_repo.get_show_by_show_id(show_id)
    if not show:
        raise NotFoundError("Show not found")
    booked_tickets = show_repo.get_booked_ticket(show.id)
    booked_seat_codes = [ticket.seat_code for ticket in booked_tickets]
    day_type = 'WEEKEND' if show.start_time.isoweekday() >= 6 else "WEEKDAY"

    seats_data = []
    for seat in show.room.seats:
        seats_data.append({
            "code": seat.code,
            "row": seat.row,
            "col": seat.column,
            "type": seat.type.value,
            "price": int(show_repo.get_price_seats(f"{seat.type.value}_{day_type}").value),
            "is_booked": seat.code in booked_seat_codes
        })


    return {
        "film_title": show.film.title,
        "cinema_name": show.room.cinema.name,
        "address": show.room.cinema.address,
        "poster": show.film.poster,
        "room_name": show.room.name,
        "start_time": show.start_time.strftime("%Hh%M' %d/%m/%Y"),
        "seats": seats_data
    }