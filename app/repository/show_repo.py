from app.models import Show, Ticket, Rules
from app.utils.errors import NotFoundError


def get_show_by_show_id(show_id):
    return Show.query.filter_by(id=show_id).first()

def get_booked_ticket(show_id):
    return Ticket.query.filter_by(show_id=show_id, active=True).all()

def get_price_seats(name:str):
    rules = Rules.query.filter_by(name=name).first()
    if not rules:
        raise NotFoundError(f"No rule with name {name}")
    return rules