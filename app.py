import random
from datetime import datetime, timedelta
from faker import Faker
from app import db
from app.models import (
    User, RoleEnum, Cinema, Room, Seat, SeatType,
    Film, Show
)

fake = Faker('vi_VN')


def seed_data():
    print("--- Đang xóa và khởi tạo lại cấu trúc Database ---")
    db.drop_all()
    db.create_all()

    # 1. Tạo Users
    print("--- Đang tạo Users ---")
    admin = User(
        username="admin",
        password="123",
        full_name="Hào Admin",
        role=RoleEnum.ADMIN
    )
    db.session.add(admin)

    for _ in range(10):
        u = User(
            username=fake.user_name(),
            password="123",
            full_name=fake.name(),
            email=fake.email(),
            role=RoleEnum.USER
        )
        db.session.add(u)
    db.session.commit()

    # 2. Tạo Cinemas & Rooms (Mỗi phòng 80 ghế)
    print("--- Đang tạo Rạp & 80 Ghế/Phòng ---")
    for _ in range(2):
        cinema = Cinema(
            name=f"CineFlow {fake.city()}",
            address=fake.address(),
            hotline=fake.phone_number()[:20]
        )
        db.session.add(cinema)
        db.session.flush()

        for i in range(2):
            room = Room(name=f"Phòng chiếu {i + 1}", cinema_id=cinema.id)
            db.session.add(room)
            db.session.flush()

            # Tạo 80 ghế: 8 hàng (A-H), mỗi hàng 10 cột
            # Theo quy tắc: Hàng A->F là SINGLE, G->H là COUPLE
            rows = ['A', 'B', 'C', 'D', 'E', 'F', 'G', 'H']
            for r_code in rows:
                for c in range(1, 11):
                    s_type = SeatType.COUPLE if r_code in ['G', 'H'] else SeatType.SINGLE
                    seat = Seat(
                        code=f"C{cinema.id}R{room.id}-{r_code}{c}",
                        type=s_type,
                        row=r_code,
                        column=c,
                        room_id=room.id
                    )
                    db.session.add(seat)
    db.session.commit()

    # 3. Tạo Films (Chiếu gần đây)
    print("--- Đang tạo Phim ---")
    films = []
    for _ in range(8):
        f = Film(
            title=fake.catch_phrase(),
            description=fake.text(),
            genre=random.choice(['Hành động', 'Hài hước', 'Kinh dị', 'Tình cảm']),
            duration=random.randint(90, 150),
            release_date=datetime.now() - timedelta(days=15),
            expired_date=datetime.now() + timedelta(days=15),
            poster="https://res.cloudinary.com/ds11ggie4/image/upload/v1773936958/tho-oi-29301-thumb_tpu4bj.webp"
        )
        films.append(f)
        db.session.add(f)
    db.session.commit()

    # 4. Tạo Suất chiếu (Gần đây: Hôm qua, Hôm nay, Ngày mai)
    print("--- Đang tạo Suất chiếu ---")
    rooms = Room.query.all()
    for room in rooms:
        # Mỗi phòng tạo suất chiếu trong 3 ngày
        for day_off in [-1, 0, 1]:
            # Tạo 2 suất chiếu mỗi ngày cho mỗi phòng
            for hour in [14, 19]:
                st = datetime.now().replace(hour=hour, minute=0, second=0, microsecond=0) + timedelta(days=day_off)
                show = Show(
                    start_time=st,
                    film_id=random.choice(films).id,
                    room_id=room.id
                )
                db.session.add(show)

    db.session.commit()
    print(f"--- Hoàn tất! Đã tạo xong {len(rooms)} phòng (mỗi phòng 80 ghế) và các suất chiếu gần đây. ---")


if __name__ == "__main__":
    from app import app

    with app.app_context():
        seed_data()