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
        db.session.flush()

        for i in range(3):
            room = Room(name=f"P0{i + 1}", cinema_id=cinema.id)
            db.session.add(room)
            db.session.flush()

            # --- PHẦN ĐIỀU CHỈNH TẠO GHẾ ---

            # 1. Tạo hàng ghế thường (A, B, C, D) - 12 cột, bỏ cột 3 & 4
            for r in ['A', 'B', 'C', 'D']:
                for c in range(1, 13):
                    if c in [3, 4]:  # Bỏ qua cột 3 và 4
                        continue

                    seat = Seat(
                        code=f"{cinema.id}-{room.id}-{r}{c}",
                        type=SeatType.SINGLE,
                        row=r,
                        column=c,
                        room_id=room.id
                    )
                    db.session.add(seat)

            # 2. Tạo 1 hàng ghế đôi (Hàng E) - 5 ghế
            for c in range(1, 6):
                seat = Seat(
                    code=f"{cinema.id}-{room.id}-E{c}",
                    type=SeatType.COUPLE,
                    row='E',
                    column=c,
                    room_id=room.id
                )
                db.session.add(seat)

            # ------------------------------

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
            poster="https://res.cloudinary.com/ds11ggie4/image/upload/v1773936958/tho-oi-29301-thumb_tpu4bj.webp",
            duration=random.randint(90, 150)
        )
        films.append(film)
        db.session.add(film)
    db.session.commit()

    print("--- Đang tạo Suất chiếu ---")
    rooms = Room.query.all()
    films = Film.query.all()

    # Cấu hình các khung giờ bắt đầu dự kiến (ví dụ từ 8h sáng đến 11h đêm)
    start_hours = [8, 11, 14, 17, 20, 23]

    for room in rooms:
        # Tạo suất chiếu cho 7 ngày tới
        for day_offset in range(7):
            current_date = datetime.now().date() + timedelta(days=day_offset)

            for hour in start_hours:
                # Thêm một chút ngẫu nhiên về phút (0, 15, 30) để nhìn thực tế hơn
                minute = random.choice([0, 15, 30, 45])
                show_time = datetime.combine(current_date, datetime.min.time()).replace(
                    hour=hour,
                    minute=minute
                )

                # Tránh tạo suất chiếu trong quá khứ nếu là ngày hôm nay
                if show_time < datetime.now():
                    continue

                show = Show(
                    start_time=show_time,
                    film_id=random.choice(films).id,
                    room_id=room.id
                )
                db.session.add(show)

    db.session.commit()
    # 5. Tạo Bookings, Tickets & Payments


    db.session.commit()
    print("--- Đã hoàn tất tạo dữ liệu mẫu! ---")


if __name__ == "__main__":

        # Import biến app từ file khởi tạo của bạn (giả sử là app.py hoặc từ package app)
        from app import app

        with app.app_context():
            seed_data()