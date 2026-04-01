import random
from datetime import datetime, timedelta
from faker import Faker
from app import db
from app.models.user import User,UserAuthMethod,RoleEnum
from app.models.booking import Payment, PaymentStatus, PaymentType, Booking, BookingStatus, BookingPaymentStatus, Ticket
from app.models.cinema import Cinema, Room, Seat, SeatType
from app.models.film import Film



from app.models import (
    User, RoleEnum, Cinema, Room, Seat, SeatType,
    Film, Show, Booking, Ticket, Payment,
    BookingStatus, BookingPaymentStatus, PaymentStatus, PaymentType
)

fake = Faker()


def seed_data():
    print("--- Đang xóa dữ liệu cũ ---")
    db.drop_all()
    db.create_all()

    # 1. Tạo Users (1 Admin, 50 Users)
    print("--- Đang tạo Users ---")
    admin = User(
        username="admin",
        password="hashed_password",
        full_name="System Admin",
        role=RoleEnum.ADMIN
    )
    db.session.add(admin)

    users = []
    for _ in range(5):
        user = User(
            username=fake.user_name(),
            password="123456",
            full_name=fake.name(),
            phone_number=fake.phone_number()[:15],
            email=fake.email(),
            role=RoleEnum.USER
        )
        users.append(user)
        db.session.add(user)
    db.session.commit()

    # 2. Tạo Cinemas & Rooms & Seats
    print("--- Đang tạo Cinemas & Rooms ---")
    cinemas = []
    for _ in range(5):
        cinema = Cinema(
            name=f"Cinema {fake.city()}",
            address=fake.address(),
            province=fake.state(),
            hotline=fake.phone_number()[:20]
        )
        db.session.add(cinema)
        cinemas.append(cinema)
        db.session.flush()  # Để lấy cinema.id

        # Mỗi Cinema có 3 phòng chiếu
        for i in range(3):
            room = Room(name=f"P0{i + 1}", cinema_id=cinema.id)
            db.session.add(room)
            db.session.flush()

            # Tạo ghế cho mỗi phòng (5 hàng x 5 cột = 25 ghế)
            for r in ['A', 'B', 'C', 'D', 'E']:
                for c in range(1, 6):
                    seat = Seat(
                        code=f"{cinema.id}-{room.id}-{r}{c}",
                        type=SeatType.SINGLE if r != 'E' else SeatType.COUPLE,
                        row=r,
                        column=c,
                        room_id=room.id
                    )
                    db.session.add(seat)
    db.session.commit()

    # 3. Tạo Films
    print("--- Đang tạo Phim ---")
    films = []
    genres = ['Action', 'Comedy', 'Horror', 'Sci-Fi', 'Drama']
    for _ in range(10):
        film = Film(
            title=fake.catch_phrase(),
            description=fake.text(),
            genre=random.choice(genres),
            age_limit=random.choice([13, 16, 18]),
            release_date=fake.date_between(start_date='-1y', end_date='today'),
            expired_date=fake.date_between(start_date='today', end_date='+1y'),
            poster="https://via.placeholder.com/300x450",
            duration=random.randint(90, 150)
        )
        films.append(film)
        db.session.add(film)
    db.session.commit()

    # 4. Tạo Shows (Mỗi phòng chiếu 2 suất mỗi ngày)
    print("--- Đang tạo Suất chiếu ---")
    shows = []
    rooms = Room.query.all()
    for room in rooms:
        for i in range(2):
            show = Show(
                start_time=datetime.now() + timedelta(days=random.randint(1, 7), hours=random.randint(8, 22)),
                film_id=random.choice(films).id,
                room_id=room.id
            )
            shows.append(show)
            db.session.add(show)
    db.session.commit()

    # 5. Tạo Bookings, Tickets & Payments
    print("--- Đang tạo Bookings & Tickets ---")
    for _ in range(100):
        selected_user = random.choice(users)
        selected_show = random.choice(shows)

        # Lấy ngẫu nhiên 1-2 ghế trong phòng của suất chiếu đó
        available_seats = Seat.query.filter_by(room_id=selected_show.room_id).limit(2).all()

        booking_code = fake.bothify(text='BK######').upper()
        new_booking = Booking(
            code=booking_code,
            user_id=selected_user.id,
            total_price=len(available_seats) * 75000.0,
            status=BookingStatus.BOOKED,
            payment_status=BookingPaymentStatus.PAID,
            qr_code=f"QR_{booking_code}"
        )
        db.session.add(new_booking)

        # Tạo vé tương ứng
        for s in available_seats:
            ticket = Ticket(
                show_id=selected_show.id,
                seat_code=s.code,
                booking_code=booking_code,
                active=True
            )
            db.session.add(ticket)

        # Tạo thanh toán
        payment = Payment(
            code=fake.bothify(text='PAY####').upper(),
            booking_code=booking_code,
            payment_method="Momo",
            transaction_id=fake.uuid4(),
            amount=new_booking.total_price,
            status=PaymentStatus.SUCCESS,
            type=PaymentType.PAYMENT
        )
        db.session.add(payment)

    db.session.commit()
    print("--- Đã hoàn tất tạo dữ liệu mẫu! ---")


if __name__ == "__main__":

        # Import biến app từ file khởi tạo của bạn (giả sử là app.py hoặc từ package app)
        from app import app

        with app.app_context():
            seed_data()