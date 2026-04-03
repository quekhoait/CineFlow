#Chạy file này để tạo dữ liệu giả trong db

from datetime import date, datetime, timedelta
from app import db, app
from app.models import Film, Cinema, Room, Show


def seed_all_data():
    with app.app_context():
        # Xóa dữ liệu cũ theo thứ tự ngược để tránh lỗi khóa ngoại (tùy chọn)
        db.session.query(Show).delete()
        db.session.query(Room).delete()
        db.session.query(Cinema).delete()
        db.session.query(Film).delete()

        now = datetime.now()
        today = date.today()

        # --- 1. SEED FILMS (10 phim) ---
        films_data = [
            {"title": "Quỷ Nhập Tràng 2",
             "poster": "https://res.cloudinary.com/ds11ggie4/image/upload/v1773936958/tho-oi-29301-thumb_tpu4bj.webp",
             "genre": "Kinh dị", "age_limit": 18, "release_date": today - timedelta(days=10),
             "expired_date": today + timedelta(days=20), "duration": 115, "description": "Nỗi kinh hoàng trở lại."},
            {"title": "Hành Tinh Cát: Phần 2",
             "poster": "https://res.cloudinary.com/ds11ggie4/image/upload/v1773936958/tho-oi-29301-thumb_tpu4bj.webp",
             "genre": "Viễn tưởng", "age_limit": 13, "release_date": today - timedelta(days=30),
             "expired_date": today + timedelta(days=5), "duration": 166, "description": "Paul Atreides trả thù."},
            {"title": "Mai",
             "poster": "https://res.cloudinary.com/ds11ggie4/image/upload/v1773936958/tho-oi-29301-thumb_tpu4bj.webp",
             "genre": "Tâm lý", "age_limit": 18, "release_date": today - timedelta(days=5),
             "expired_date": today + timedelta(days=25), "duration": 131, "description": "Câu chuyện về Mai."},
            {"title": "Kung Fu Panda 4",
             "poster": "https://res.cloudinary.com/ds11ggie4/image/upload/v1773936958/tho-oi-29301-thumb_tpu4bj.webp",
             "genre": "Hoạt hình", "age_limit": 0, "release_date": today - timedelta(days=2),
             "expired_date": today + timedelta(days=40), "duration": 94, "description": "Po trở lại."},
            {"title": "Godzilla x Kong",
             "poster": "https://res.cloudinary.com/ds11ggie4/image/upload/v1773936958/tho-oi-29301-thumb_tpu4bj.webp",
             "genre": "Hành động", "age_limit": 13, "release_date": today - timedelta(days=15),
             "expired_date": today + timedelta(days=15), "duration": 113, "description": "Đế chế mới."},
            {"title": "Deadpool & Wolverine",
             "poster": "https://res.cloudinary.com/ds11ggie4/image/upload/v1773936958/tho-oi-29301-thumb_tpu4bj.webp",
             "genre": "Hành động", "age_limit": 18, "release_date": today + timedelta(days=10),
             "expired_date": today + timedelta(days=40), "duration": 127, "description": "MCU kết hợp."},
            {"title": "Joker: Folie à Deux",
             "poster": "https://res.cloudinary.com/ds11ggie4/image/upload/v1773936958/tho-oi-29301-thumb_tpu4bj.webp",
             "genre": "Tâm lý", "age_limit": 18, "release_date": today + timedelta(days=25),
             "expired_date": today + timedelta(days=60), "duration": 140, "description": "Arthur Fleck điên loạn."},
            {"title": "Moana 2",
             "poster": "https://res.cloudinary.com/ds11ggie4/image/upload/v1773936958/tho-oi-29301-thumb_tpu4bj.webp",
             "genre": "Hoạt hình", "age_limit": 0, "release_date": today + timedelta(days=45),
             "expired_date": today + timedelta(days=90), "duration": 105, "description": "Hành trình mới."},
            {"title": "Gladiator II",
             "poster": "https://res.cloudinary.com/ds11ggie4/image/upload/v1773936958/tho-oi-29301-thumb_tpu4bj.webp",
             "genre": "Sử thi", "age_limit": 16, "release_date": today + timedelta(days=60),
             "expired_date": today + timedelta(days=100), "duration": 150, "description": "Võ sĩ giác đấu."},
            {"title": "Avengers: Secret Wars",
             "poster": "https://res.cloudinary.com/ds11ggie4/image/upload/v1773936958/tho-oi-29301-thumb_tpu4bj.webp",
             "genre": "Bom tấn", "age_limit": 13, "release_date": today + timedelta(days=120),
             "expired_date": today + timedelta(days=180), "duration": 185, "description": "Đa vũ trụ."}
        ]

        films = []
        for item in films_data:
            f = Film(**item)
            # Nếu model của bạn có các trường này, hãy bỏ comment:
            f.created_at = now
            f.updated_at = now
            db.session.add(f)
            films.append(f)

        # --- 2. SEED CINEMAS (2 rạp) ---
        cinemas_data = [
            {"name": "Galaxy Nguyễn Du", "address": "116 Nguyễn Du, Quận 1", "province": "Hồ Chí Minh",
             "hotline": "19001001"},
            {"name": "BHD Star Cầu Giấy", "address": "Tầng 8, TTTM Discovery", "province": "Hà Nội",
             "hotline": "19002002"}
        ]
        cinemas = []
        for item in cinemas_data:
            c = Cinema(**item)
            db.session.add(c)
            cinemas.append(c)

        db.session.flush()  # Để lấy ID của Cinema cho bảng Room

        # --- 3. SEED ROOMS (4 phòng) ---
        rooms_data = [
            {"name": "P01 - IMAX", "capacity": 150, "cinema_id": cinemas[0].id},
            {"name": "P02 - 2D", "capacity": 100, "cinema_id": cinemas[0].id},
            {"name": "Room A", "capacity": 120, "cinema_id": cinemas[1].id},
            {"name": "Room B (VIP)", "capacity": 40, "cinema_id": cinemas[1].id}
        ]
        rooms = []
        for item in rooms_data:
            r = Room(**item)
            db.session.add(r)
            rooms.append(r)

        db.session.flush()  # Để lấy ID của Film và Room cho bảng Show

        # --- 4. SEED SHOWS (10 suất chiếu) ---
        # Phân bổ các phim đang chiếu vào các phòng
        shows_data = [
            {"start_time": datetime.combine(today, datetime.min.time()).replace(hour=9, minute=0),
             "film_id": films[0].id, "room_id": rooms[0].id},
            {"start_time": datetime.combine(today, datetime.min.time()).replace(hour=13, minute=0),
             "film_id": films[0].id, "room_id": rooms[1].id},
            {"start_time": datetime.combine(today, datetime.min.time()).replace(hour=19, minute=0),
             "film_id": films[1].id, "room_id": rooms[0].id},
            {"start_time": datetime.combine(today, datetime.min.time()).replace(hour=21, minute=30),
             "film_id": films[2].id, "room_id": rooms[2].id},
            {"start_time": datetime.combine(today + timedelta(days=1), datetime.min.time()).replace(hour=10, minute=0),
             "film_id": films[3].id, "room_id": rooms[3].id},
            {"start_time": datetime.combine(today + timedelta(days=1), datetime.min.time()).replace(hour=14, minute=0),
             "film_id": films[4].id, "room_id": rooms[0].id},
            {"start_time": datetime.combine(today + timedelta(days=1), datetime.min.time()).replace(hour=18, minute=0),
             "film_id": films[0].id, "room_id": rooms[2].id},
            {"start_time": datetime.combine(today + timedelta(days=2), datetime.min.time()).replace(hour=8, minute=0),
             "film_id": films[1].id, "room_id": rooms[1].id},
            {"start_time": datetime.combine(today + timedelta(days=2), datetime.min.time()).replace(hour=20, minute=0),
             "film_id": films[2].id, "room_id": rooms[0].id},
            {"start_time": datetime.combine(today + timedelta(days=2), datetime.min.time()).replace(hour=15, minute=0),
             "film_id": films[3].id, "room_id": rooms[3].id}
        ]

        for item in shows_data:
            s = Show(**item)
            db.session.add(s)

        db.session.commit()
        print(">>> Đã seed thành công Film, Cinema, Room và Show!")


if __name__ == "__main__":
    seed_all_data()