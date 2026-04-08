from datetime import datetime, timedelta, date
from werkzeug.security import generate_password_hash

def seed_data(app, db):
    from app.models.user import User, RoleEnum
    from app.models.rules import Rules
    from app.models.film import Film, Show
    from app.models.cinema import Cinema, Room, Seat, SeatType
    from app.models.booking import Booking, Ticket, Payment, BookingStatus, BookingPaymentStatus, PaymentStatus, \
        PaymentType
    with app.app_context():
        print("Đang xóa dữ liệu cũ và tạo lại bảng...")
        db.drop_all()
        db.create_all()

        print("Đang tạo Admin...")
        admin = User(
            username='admin',
            password=generate_password_hash('Admin123@'),
            full_name='Quản Trị Viên CineFlow',
            email='admin@cineflow.vn',
            role=RoleEnum.ADMIN,
            is_active=True
        )
        db.session.add(admin)
        db.session.commit()
        print("Đang tạo Rules...")
        rules_data = [
            ("SINGLE_WEEKDAY", "VND", "50000", True),
            ("SINGLE_WEEKEND", "VND", "65000", True),
            ("COUPLE_WEEKDAY", "VND", "100000", True),
            ("COUPLE_WEEKEND", "VND", "125000", True),
        ]
        for name, r_type, value, active in rules_data:
            rule = Rules(name=name, type=r_type, value=value, active=active, user_id=admin.id)
            db.session.add(rule)
        db.session.commit()

        films_data = [
            Film(title='The Batman Part II (2026)',
                 description='Hiệp sĩ bóng đêm Bruce Wayne tiếp tục hành trình bảo vệ Gotham khỏi những thế lực tội phạm mới.',
                 genre='Action, Crime', age_limit=16, release_date=date(2026, 3, 2), expired_date=date(2026, 11, 30),
                 poster='https://image.tmdb.org/t/p/w500/74xTEgt7R36Fpooo50r9T25onhq.jpg', duration=140),
            Film(title='Avengers: Doomsday (2026)',
                 description='Biệt đội siêu anh hùng Avengers tập hợp để đối mặt với một mối đe dọa đa vũ trụ cực lớn.',
                 genre='Action, Sci-Fi', age_limit=13, release_date=date(2026, 3, 1), expired_date=date(2026, 7, 30),
                 poster='https://image.tmdb.org/t/p/w500/or06FN3Dka5tukK1e9sl16pB3iy.jpg', duration=150),
            Film(title='Toy Story 5',
                 description='Woody, Buzz Lightyear và những người bạn đồ chơi trở lại với một cuộc phiêu lưu hoàn toàn mới.',
                 genre='Animation, Family', age_limit=0, release_date=date(2026, 3, 19), expired_date=date(2026, 8, 20),
                 poster='https://image.tmdb.org/t/p/w500/w9kR8qbmQ01HwnvK4alvnQ2ca0L.jpg', duration=100),
            Film(title='Supergirl: Woman of Tomorrow',
                 description='Câu chuyện hoành tráng về Kara Zor-El trên hành trình khám phá sức mạnh và sứ mệnh của bản thân.',
                 genre='Action, Adventure', age_limit=13, release_date=date(2026, 3, 26), expired_date=date(2026, 9, 1),
                 poster='https://image.tmdb.org/t/p/w500/wsaXEAOqS4G0Gq2bE1QvWzPmsE6.jpg', duration=120)
        ]
        db.session.add_all(films_data)
        db.session.commit()

        print("Đang tạo Rạp, Phòng chiếu và Ma trận Ghế...")
        cinemas_data = [
            ('CineFlow Hà Nội', '119 Trần Duy Hưng, Cầu Giấy', 'Hà Nội', '19001001'),
            ('CineFlow Đà Nẵng', '74 Bạch Đằng, Hải Châu', 'Đà Nẵng', '19001002'),
            ('CineFlow Hồ Chí Minh', '12 Lê Lợi, Quận 1', 'Hồ Chí Minh', '19001003')
        ]
        cinemas = []
        for name, address, prov, hotline in cinemas_data:
            c = Cinema(name=name, address=address, province=prov, hotline=hotline)
            db.session.add(c)
            cinemas.append(c)
        db.session.commit()

        for cinema in cinemas:
            for i in range(1, 4):
                room = Room(name=f'Phòng {i}', row=7, column=12, cinema_id=cinema.id)
                db.session.add(room)
                db.session.commit()

                for r_idx in range(ord('A'), ord('H')):
                    row_char = chr(r_idx)

                    if row_char in ['F', 'G']:
                        for col in range(1, 6):
                            seat_code = f"C{cinema.id}R{room.id}-{row_char}{col}"
                            seat = Seat(code=seat_code, type=SeatType.COUPLE, row=row_char, column=col, room_id=room.id)
                            db.session.add(seat)

                    else:
                        for col in range(1, 13):
                            if col in [4, 9]:
                                continue

                            seat_code = f"C{cinema.id}R{room.id}-{row_char}{col}"
                            seat = Seat(code=seat_code, type=SeatType.SINGLE, row=row_char, column=col, room_id=room.id)
                            db.session.add(seat)
                db.session.commit()

        print("Đang tạo Lịch chiếu...")
        today = datetime.now()
        rooms = Room.query.all()
        for film in films_data:
            for room in rooms:
                for day_offset in range(7):
                    show_date = today + timedelta(days=day_offset)

                    show1 = Show(start_time=show_date.replace(hour=14, minute=0, second=0, microsecond=0),
                                 film_id=film.id, room_id=room.id)
                    show2 = Show(start_time=show_date.replace(hour=19, minute=30, second=0, microsecond=0),
                                 film_id=film.id, room_id=room.id)
                    db.session.add_all([show1, show2])
        db.session.commit()

        print("Đang tạo Dữ liệu Đặt vé mẫu...")
        customer = User(username='khachhang1', password=generate_password_hash('Khach123!'), full_name='Khách Hàng',
                        email='khach@cineflow.vn', role=RoleEnum.USER, is_active=True)
        db.session.add(customer)
        db.session.commit()

        first_show = Show.query.first()
        seats = Seat.query.filter_by(room_id=first_show.room_id, type=SeatType.SINGLE).limit(2).all()

        booking = Booking(code='BK000001', user_id=customer.id, total_price=100000, status=BookingStatus.BOOKED,
                          payment_status=BookingPaymentStatus.PAID)
        db.session.add(booking)
        db.session.commit()

        for seat in seats:
            ticket = Ticket(show_id=first_show.id, seat_code=seat.code, booking_code=booking.code, price=50000,
                            active=True)
            db.session.add(ticket)

        payment = Payment(code='PAY000000001', booking_code=booking.code, payment_method='VNPay', amount=100000,
                          status=PaymentStatus.SUCCESS, type=PaymentType.PAYMENT)
        db.session.add(payment)
        db.session.commit()

        print("\nHoàn tất! Dữ liệu giả đã được thêm thành công vào Database.")
