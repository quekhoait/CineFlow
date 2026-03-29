from app.repository import show_repo


def get_show_seats_info(show_id):
    return show_repo.get_show_seats(show_id)