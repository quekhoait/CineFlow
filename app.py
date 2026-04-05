import random
from datetime import datetime, timedelta
from faker import Faker
from app import db, app
from app.models import Cinema, Room, Seat, SeatType, Film, Show

fake = Faker('vi_VN')


def seed_data():
    print("--- 1. Xóa và khởi tạo lại Database ---")
    db.drop_all()
    db.create_all()

    # 2. Tạo Rạp & Phòng (Giữ nguyên 2 rạp, mỗi rạp 2 phòng)
    print("--- 2. Đang tạo Rạp & Ghế ---")
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

            # Tạo 80 ghế/phòng
            rows = ['A', 'B', 'C', 'D', 'E', 'F', 'G', 'H']
            for r_code in rows:
                for c in range(1, 11):
                    s_type = SeatType.COUPLE if r_code in ['G', 'H'] else SeatType.SINGLE
                    db.session.add(Seat(
                        code=f"C{cinema.id}R{room.id}-{r_code}{c}",
                        type=s_type, row=r_code, column=c, room_id=room.id
                    ))
    db.session.commit()

    # 3. Tạo 40 Phim (20 Đang chiếu, 20 Sắp chiếu)
    print("--- 3. Đang tạo 40 Phim ---")
    base_now = datetime(2026, 4, 5, 8, 0, 0)
    films = []
    for i in range(40):
        is_showing = i < 20
        rel = (base_now - timedelta(days=random.randint(1, 10))).date() if is_showing else (
                    base_now + timedelta(days=random.randint(2, 10))).date()
        exp = rel + timedelta(days=30)

        f = Film(
            title=fake.catch_phrase() + (" (Đang chiếu)" if is_showing else " (Sắp tới)"),
            description=fake.text(max_nb_chars=100),
            genre=random.choice(['Hành động', 'Hài', 'Kinh dị', 'Tình cảm']),
            duration=random.randint(90, 130),  # Thời lượng phim để tính lịch
            age_limit=random.choice([0, 13, 16, 18]),
            release_date=rel, expired_date=exp,
            poster="https://res.cloudinary.com/ds11ggie4/image/upload/v1773936958/tho-oi-29301-thumb_tpu4bj.webp"
        )
        films.append(f)
        db.session.add(f)
    db.session.commit()

    # 4. Lấp đầy suất chiếu (Mọi phim đang chiếu đều có nhiều suất)
    print("--- 4. Đang lấp đầy lịch chiếu cho tất cả các phòng ---")
    rooms = Room.query.all()
    showing_films = [f for f in films if "Đang chiếu" in f.title]

    show_count = 0
    # Tạo lịch cho 7 ngày
    for day_offset in range(7):
        for room in rooms:
            # Bắt đầu từ 8:00 sáng mỗi ngày
            current_time = base_now.replace(hour=8, minute=0) + timedelta(days=day_offset)

            # Lấp đầy cho đến 23:30 đêm
            while current_time.hour < 23:
                film = random.choice(showing_films)

                # Tạo suất chiếu
                new_show = Show(
                    start_time=current_time,
                    film_id=film.id,
                    room_id=room.id
                )
                db.session.add(new_show)
                show_count += 1

                # Tính thời gian cho suất tiếp theo:
                # Thời lượng phim + 30 phút nghỉ/dọn phòng
                gap = film.duration + 30
                current_time += timedelta(minutes=gap)

    db.session.commit()
    print(f"--- HOÀN TẤT: Đã tạo {show_count} suất chiếu san sát nhau cho tất cả phim! ---")


if __name__ == "__main__":
    with app.app_context():
        seed_data()