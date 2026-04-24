from datetime import datetime, timedelta, date
from werkzeug.security import generate_password_hash
from app import db, models


def run_seeding():
    print("Drop dataset before seeding...")
    db.drop_all()
    db.create_all()

    print('Create admin')
    admin = models.User(
        username='admin',
        full_name='Trần Quốc Tuấn',
        phone_number='+15555555555',
        email='admin@cineflow.me',
        password=generate_password_hash('Abc123@'),
        role=models.RoleEnum.ADMIN
    )
    db.session.add(admin)
    db.session.flush()

    admin_auth = models.UserAuthMethod(
        user_id=admin.id,
        provider="EMAIL",
        provider_id=admin.email,
    )
    db.session.add(admin_auth)
    db.session.commit()

    print("Create Rules Table...")
    rules_data = [
        ("SINGLE_WEEKDAY", "VND", "50000", True),
        ("SINGLE_WEEKEND", "VND", "65000", True),
        ("COUPLE_WEEKDAY", "VND", "100000", True),
        ("COUPLE_WEEKEND", "VND", "125000", True),
    ]
    for name, r_type, value, active in rules_data:
        rule = models.Rules(name=name, type=r_type, value=value, active=active, user_id=admin.id)
        db.session.add(rule)
    db.session.commit()

    films_data = [
        models.Film(title='The Batman Part II (2026)',
                    description='Hiệp sĩ bóng đêm Bruce Wayne tiếp tục hành trình bảo vệ Gotham khỏi những thế lực tội phạm mới.',
                    genre='Action, Crime', age_limit=16, release_date=date(2026, 3, 2), expired_date=date(2026, 11, 30),
                    poster='https://image.tmdb.org/t/p/w500/74xTEgt7R36Fpooo50r9T25onhq.jpg', duration=140),
        models.Film(title='Avengers: Doomsday (2026)',
                    description='Biệt đội siêu anh hùng Avengers tập hợp để đối mặt với một mối đe dọa đa vũ trụ cực lớn.',
                    genre='Action, Sci-Fi', age_limit=13, release_date=date(2026, 3, 1), expired_date=date(2026, 7, 30),
                    poster='https://image.tmdb.org/t/p/w500/or06FN3Dka5tukK1e9sl16pB3iy.jpg', duration=150),
        models.Film(title='Toy Story 5',
                    description='Woody, Buzz Lightyear và những người bạn đồ chơi trở lại với một cuộc phiêu lưu hoàn toàn mới.',
                    genre='Animation, Family', age_limit=0, release_date=date(2026, 3, 19),
                    expired_date=date(2026, 8, 20),
                    poster='https://image.tmdb.org/t/p/w500/w9kR8qbmQ01HwnvK4alvnQ2ca0L.jpg', duration=100),
        models.Film(title='Supergirl: Woman of Tomorrow',
                    description='Câu chuyện hoành tráng về Kara Zor-El trên hành trình khám phá sức mạnh và sứ mệnh của bản thân.',
                    genre='Action, Adventure', age_limit=13, release_date=date(2026, 3, 26),
                    expired_date=date(2026, 9, 1),
                    poster='https://m.media-amazon.com/images/I/81WCblz7GnL._AC_UF1000,1000_QL80_.jpg', duration=120)
    ]
    db.session.add_all(films_data)
    db.session.commit()

    print("Create room and seats...")
    cinemas_info = [
        {'name': 'CineFlow Hà Nội', 'city': 'Hà Nội', 'films': [0, 1, 2, 3]},
        {'name': 'CineFlow Đà Nẵng', 'city': 'Đà Nẵng', 'films': [0, 2]},
        {'name': 'CineFlow Hồ Chí Minh', 'city': 'Hồ Chí Minh', 'films': [1, 3]}
    ]
    for info in cinemas_info:
        cinema = models.Cinema(name=info['name'], province=info['city'], address="Địa chỉ hệ thống", hotline="19001000")
        db.session.add(cinema)
        db.session.commit()

        for p_idx in range(1, 4):
            room = models.Room(name=f'Phòng {p_idx}', row=7, column=12, cinema_id=cinema.id)
            db.session.add(room)
            db.session.commit()

            for r_idx in range(ord('A'), ord('H')):
                row_char = chr(r_idx)

                if row_char in ['F', 'G']:
                    for col in range(1, 7):
                        seat_code = f"C{cinema.id}R{room.id}-{row_char}{col}"
                        seat = models.Seat(code=seat_code, type=models.SeatType.COUPLE, row=row_char, column=col,
                                           room_id=room.id)
                        db.session.add(seat)

                else:
                    for col in range(1, 13):
                        if col in [4, 9]:
                            continue

                        seat_code = f"C{cinema.id}R{room.id}-{row_char}{col}"
                        seat = models.Seat(code=seat_code, type=models.SeatType.SINGLE, row=row_char, column=col,
                                           room_id=room.id)
                        db.session.add(seat)
            db.session.commit()

        today = datetime.now()
        for f_idx in info['films']:
            film = films_data[f_idx]
            rooms = models.Room.query.filter_by(cinema_id=cinema.id).all()
            for room in rooms:
                for day_offset in range(3):
                    show_date = today + timedelta(days=day_offset)
                    s1 = models.Show(start_time=show_date.replace(hour=14, minute=0, second=0, microsecond=0),
                                     film_id=film.id, room_id=room.id)
                    s2 = models.Show(start_time=show_date.replace(hour=19, minute=30, second=0, microsecond=0),
                                     film_id=film.id, room_id=room.id)
                    db.session.add_all([s1, s2])
        db.session.commit()
    print("Done!!")