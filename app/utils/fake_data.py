from datetime import date, datetime

def seed_data(db):
    from app.models import Film, Cinema, Room, Seat, Show
    f1 = Film(title="Dune: Part Two", poster="dune2.jpg", duration=166, age_limit=13,
              release_date=date(2026, 3, 1), expired_date=date(2026, 4, 1))

    c1 = Cinema(name="CineFlow Quận 5", address="123 Hùng Vương", province="HCM", hotline="19001234")
    db.session.add_all([f1, c1])
    db.session.commit()

    r1 = Room(name="P01", row="J", column=10, cinema_id=c1.id)
    db.session.add(r1)
    db.session.commit()

    s1 = Seat(code="R1-A1", type="NORMAL", row="A", column=1, room_id=r1.id)
    s2 = Seat(code="R1-A2", type="NORMAL", row="A", column=2, room_id=r1.id)
    db.session.add_all([s1, s2])

    sh1 = Show(start_time=datetime(2026, 3, 25, 19, 0), film_id=f1.id, room_id=r1.id)
    db.session.add(sh1)
    db.session.commit()