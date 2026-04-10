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

        from datetime import date

        films_data = [
            # --- PHIM ĐANG CHIẾU ---
            Film(title='The Batman Part II',
                 description='Hiệp sĩ bóng đêm Bruce Wayne tiếp tục hành trình bảo vệ Gotham khỏi những thế lực tội phạm mới.',
                 genre='Action, Crime', age_limit=16, release_date=date(2026, 3, 2), expired_date=date(2026, 6, 2),
                 poster='https://image.tmdb.org/t/p/w500/74xTEgt7R36Fpooo50r9T25onhq.jpg', duration=140),
            Film(title='Avengers: Doomsday',
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
                 poster='https://image.tmdb.org/t/p/w500/wsaXEAOqS4G0Gq2bE1QvWzPmsE6.jpg', duration=120),
            Film(title='Frozen III',
                 description='Anna và Elsa đối mặt với một bí ẩn cổ xưa đe dọa vương quốc Arendelle một lần nữa.',
                 genre='Animation, Musical', age_limit=0, release_date=date(2026, 1, 15),
                 expired_date=date(2026, 4, 15),
                 poster='https://image.tmdb.org/t/p/w500/8bBihToolsZ6BqxJu7vSfsstFc.jpg', duration=105),
            Film(title='The Mandalorian & Grogu',
                 description='Cuộc phiêu lưu mới của thợ săn tiền thưởng và cậu bé Grogu trong thiên hà xa xôi.',
                 genre='Sci-Fi, Adventure', age_limit=13, release_date=date(2026, 2, 10),
                 expired_date=date(2026, 5, 10),
                 poster='https://image.tmdb.org/t/p/w500/9699896711689.jpg', duration=115),
            Film(title='Spider-Man 4 (MCU)',
                 description='Peter Parker bắt đầu một chương mới trong cuộc đời sau khi thế giới quên đi danh tính của cậu.',
                 genre='Action, Sci-Fi', age_limit=13, release_date=date(2026, 3, 5), expired_date=date(2026, 6, 5),
                 poster='https://image.tmdb.org/t/p/w500/spiderman4_poster.jpg', duration=135),
            Film(title='Moana Live Action',
                 description='Phiên bản người đóng của câu chuyện về cô gái trẻ dũng cảm vượt đại dương cứu bộ tộc.',
                 genre='Adventure, Family', age_limit=0, release_date=date(2026, 3, 12), expired_date=date(2026, 6, 12),
                 poster='https://image.tmdb.org/t/p/w500/moana_live.jpg', duration=110),
            Film(title='Fast X: Part 2',
                 description='Chương cuối cùng của hành trình tốc độ đầy kịch tính của gia đình Dominic Toretto.',
                 genre='Action, Racing', age_limit=16, release_date=date(2026, 4, 1), expired_date=date(2026, 7, 1),
                 poster='https://image.tmdb.org/t/p/w500/fastx2.jpg', duration=145),
            Film(title='Zootopia 2',
                 description='Judy Hopps và Nick Wilde trở lại để giải quyết một vụ án hóc búa nhất thành phố thú cưng.',
                 genre='Animation, Comedy', age_limit=0, release_date=date(2026, 2, 14), expired_date=date(2026, 5, 14),
                 poster='https://image.tmdb.org/t/p/w500/zootopia2.jpg', duration=108),
            Film(title='The Super Mario Bros. 2',
                 description='Mario và Luigi dấn thân vào một vương quốc mới đầy rẫy những thử thách nấm lùn.',
                 genre='Animation, Adventure', age_limit=0, release_date=date(2026, 3, 30),
                 expired_date=date(2026, 6, 30),
                 poster='https://image.tmdb.org/t/p/w500/mario2.jpg', duration=95),
            Film(title='Black Panther: Wakanda',
                 description='Vương quốc Wakanda phải đối mặt với những biến động chính trị và kẻ thù mới từ đại dương.',
                 genre='Action, Drama', age_limit=13, release_date=date(2026, 4, 5), expired_date=date(2026, 7, 5),
                 poster='https://image.tmdb.org/t/p/w500/wakanda_series.jpg', duration=120),
            Film(title='Sherlock Holmes 3',
                 description='Sherlock Holmes và bác sĩ Watson tái ngộ trong một vụ án xuyên quốc gia.',
                 genre='Mystery, Action', age_limit=13, release_date=date(2026, 1, 25), expired_date=date(2026, 4, 25),
                 poster='https://image.tmdb.org/t/p/w500/sherlock3.jpg', duration=128),
            Film(title='Now You See Me 3',
                 description='Nhóm Tứ Kỵ Sĩ trở lại với những màn ảo thuật không tưởng để vạch trần tội ác.',
                 genre='Thriller, Crime', age_limit=13, release_date=date(2026, 2, 28), expired_date=date(2026, 5, 28),
                 poster='https://image.tmdb.org/t/p/w500/nysm3.jpg', duration=115),
            Film(title='Project Hail Mary',
                 description='Một phi hành gia đơn độc phải cứu nhân loại khỏi thảm họa tuyệt chủng.',
                 genre='Sci-Fi', age_limit=13, release_date=date(2026, 3, 20), expired_date=date(2026, 6, 20),
                 poster='https://image.tmdb.org/t/p/w500/hailmary.jpg', duration=130),

            # --- PHIM SẮP CHIẾU ---
            Film(title='Jurassic World 4',
                 description='Kỷ nguyên của khủng long bước sang một trang mới khi chúng thích nghi với thế giới con người.',
                 genre='Sci-Fi, Adventure', age_limit=13, release_date=date(2026, 6, 12),
                 expired_date=date(2026, 9, 12),
                 poster='https://image.tmdb.org/t/p/w500/jw4.jpg', duration=125),
            Film(title='Doctor Strange 3',
                 description='Stephen Strange phải đối mặt với hậu quả của việc xâm phạm đa vũ trụ.',
                 genre='Fantasy, Action', age_limit=13, release_date=date(2026, 5, 15), expired_date=date(2026, 8, 15),
                 poster='https://image.tmdb.org/t/p/w500/drstrange3.jpg', duration=135),
            Film(title='Avatar: Fire and Ash',
                 description='Jake Sully và Neytiri gặp gỡ một bộ tộc Na\'vi hung hãn sống trong vùng lửa.',
                 genre='Sci-Fi, Adventure', age_limit=13, release_date=date(2026, 12, 18),
                 expired_date=date(2027, 3, 18),
                 poster='https://image.tmdb.org/t/p/w500/avatar3.jpg', duration=180),
            Film(title='The Incredibles 3',
                 description='Gia đình siêu nhân đối đầu với một ác nhân mới hiểu rõ mọi điểm yếu của họ.',
                 genre='Animation, Action', age_limit=0, release_date=date(2026, 6, 20), expired_date=date(2026, 9, 20),
                 poster='https://image.tmdb.org/t/p/w500/incredibles3.jpg', duration=118),
            Film(title='John Wick: Chapter 5',
                 description='Sát thủ huyền thoại John Wick chưa thể tìm thấy sự bình yên khi kẻ thù vẫn săn đuổi.',
                 genre='Action, Thriller', age_limit=18, release_date=date(2026, 5, 22), expired_date=date(2026, 8, 22),
                 poster='https://image.tmdb.org/t/p/w500/jw5.jpg', duration=130),
            Film(title='Dune: Messiah',
                 description='Paul Atreides đối mặt với những âm mưu chính trị khi nắm giữ quyền lực tối cao.',
                 genre='Sci-Fi, Drama', age_limit=13, release_date=date(2026, 11, 20), expired_date=date(2027, 2, 20),
                 poster='https://image.tmdb.org/t/p/w500/dune3.jpg', duration=160),
            Film(title='Constantine 2',
                 description='John Constantine trở lại để xua đuổi những linh hồn quỷ dữ đang xâm chiếm London.',
                 genre='Horror, Fantasy', age_limit=16, release_date=date(2026, 10, 30), expired_date=date(2027, 1, 30),
                 poster='https://image.tmdb.org/t/p/w500/constantine2.jpg', duration=125),
            Film(title='The Conjuring: Last Rites',
                 description='Vụ án cuối cùng đầy kinh hoàng của đôi vợ chồng trừ tà nhà Warren.',
                 genre='Horror', age_limit=18, release_date=date(2026, 9, 13), expired_date=date(2026, 12, 13),
                 poster='https://image.tmdb.org/t/p/w500/conjuring4.jpg', duration=110),
            Film(title='Wicked: Part 2',
                 description='Sự thật về phù thủy tốt lành và phù thủy độc ác của xứ Oz được hé lộ.',
                 genre='Musical, Fantasy', age_limit=0, release_date=date(2026, 11, 26), expired_date=date(2027, 2, 26),
                 poster='https://image.tmdb.org/t/p/w500/wicked2.jpg', duration=140),
            Film(title='Fantastic Four',
                 description='Gia đình đầu tiên của Marvel bắt đầu hành trình bảo vệ Trái Đất.',
                 genre='Action, Sci-Fi', age_limit=13, release_date=date(2026, 5, 2), expired_date=date(2026, 8, 2),
                 poster='https://image.tmdb.org/t/p/w500/f4.jpg', duration=125),
            Film(title='Sonic the Hedgehog 4',
                 description='Sonic và những người bạn phải ngăn chặn một phát minh điên rồ của Robotnik.',
                 genre='Adventure, Comedy', age_limit=0, release_date=date(2026, 12, 20),
                 expired_date=date(2027, 3, 20),
                 poster='https://image.tmdb.org/t/p/w500/sonic4.jpg', duration=105),
            Film(title='Blade',
                 description='Thợ săn ma cà rồng Blade tái xuất trong cuộc chiến chống lại bóng tối.',
                 genre='Horror, Action', age_limit=18, release_date=date(2026, 8, 15), expired_date=date(2026, 11, 15),
                 poster='https://image.tmdb.org/t/p/w500/blade.jpg', duration=120),
            Film(title='Tron: Ares',
                 description='Một chương trình máy tính vượt ra ngoài thế giới thực với âm mưu lật đổ con người.',
                 genre='Sci-Fi', age_limit=13, release_date=date(2026, 10, 10), expired_date=date(2027, 1, 10),
                 poster='https://image.tmdb.org/t/p/w500/tron3.jpg', duration=125),
            Film(title='Pirates 6',
                 description='Cuộc săn tìm kho báu mới trên những vùng biển xa xôi và đầy nguyền rủa.',
                 genre='Adventure, Fantasy', age_limit=13, release_date=date(2026, 7, 15),
                 expired_date=date(2026, 10, 15),
                 poster='https://image.tmdb.org/t/p/w500/potc6.jpg', duration=135),
            Film(title='Shrek 5',
                 description='Shrek, Donkey và Fiona trở lại với vương quốc Xa Thật Là Xa trong một rắc rối mới.',
                 genre='Animation, Comedy', age_limit=0, release_date=date(2026, 7, 1), expired_date=date(2026, 10, 1),
                 poster='https://image.tmdb.org/t/p/w500/shrek5.jpg', duration=95)
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
