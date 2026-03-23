import json
import random
from datetime import datetime
from faker import Faker

fake = Faker()

# Cài đặt giới hạn thời gian
START_DATE = datetime(2026, 3, 23)
END_DATE = datetime(2026, 6, 1)

def random_date():
    return fake.date_time_between(start_date=START_DATE, end_date=END_DATE).strftime('%Y-%m-%dT%H:%M:%S')

def random_date_only():
    return fake.date_between(start_date=START_DATE, end_date=END_DATE).strftime('%Y-%m-%d')

data = {
    "user": [], "cinema": [], "room": [], "seat": [], "film": [],
    "show": [], "show_seat": [], "booking": [], "ticket": [],
    "payment": [], "rules": [], "user_auth_method": []
}

# 1. Bảng User (Có Avatar thật)
for i in range(1, 101):
    data["user"].append({
        "id": i,
        "username": fake.unique.user_name(),
        "password": "pbkdf2:sha256:260000$dummyhash",
        "full_name": fake.name(),
        "phone_number": fake.numerify('09########'),
        "email": fake.unique.email(),
        "avatar": f"https://i.pravatar.cc/150?u={i}", # Hình ảnh thật
        "role": random.choice(["ADMIN", "USER"]),
        "is_active": True,
        "created_at": random_date(),
        "updated_at": random_date()
    })

# 2. Bảng Cinema
for i in range(1, 101):
    data["cinema"].append({
        "id": i,
        "name": f"CineFlow {fake.city()}",
        "address": fake.address().replace('\n', ', '),
        "province": fake.city(),
        "hotline": fake.numerify('1900####'),
        "created_at": random_date(),
        "updated_at": random_date()
    })

# 3. Bảng Room
for i in range(1, 101):
    data["room"].append({
        "id": i,
        "name": f"Room {random.randint(1, 10)}",
        "capacity": random.randint(50, 200),
        "cinema_id": random.randint(1, 100), # Trỏ về 100 cinema
        "created_at": random_date(),
        "updated_at": random_date()
    })

# 4. Bảng Seat
for i in range(1, 101):
    data["seat"].append({
        "code": f"S{i}-R{random.choice(['A', 'B', 'C', 'D'])}{random.randint(1,20)}",
        "type": random.choice(["NORMAL", "VIP", "COUPLE"]),
        "row": random.choice(['A', 'B', 'C', 'D']),
        "column": random.randint(1, 20),
        "room_id": random.randint(1, 100),
        "created_at": random_date(),
        "updated_at": random_date()
    })

# 5. Bảng Film (Có Poster thật)
for i in range(1, 101):
    data["film"].append({
        "id": i,
        "title": fake.catch_phrase(),
        "poster": f"https://picsum.photos/seed/film{i}/400/600", # Hình ảnh thật
        "description": fake.text(max_nb_chars=200),
        "genre": random.choice(["Action", "Sci-Fi", "Drama", "Comedy", "Horror"]),
        "age_limit": random.choice([0, 13, 16, 18]),
        "release_date": random_date_only(),
        "expired_date": random_date_only(),
        "duration": random.randint(90, 180),
        "created_at": random_date(),
        "updated_at": random_date()
    })

# 6. Bảng Show
for i in range(1, 101):
    data["show"].append({
        "id": i,
        "start_time": random_date(),
        "film_id": random.randint(1, 100),
        "room_id": random.randint(1, 100),
        "created_at": random_date(),
        "updated_at": random_date()
    })

# 7. Bảng ShowSeat
for i in range(1, 101):
    data["show_seat"].append({
        "id": i,
        "show_id": random.randint(1, 100),
        "seat_code": data["seat"][random.randint(0, 99)]["code"],
        "status": random.choice(["AVAILABLE", "HOLD", "BOOKED"]),
        "created_at": random_date(),
        "updated_at": random_date()
    })

# 8. Bảng Booking
for i in range(1, 101):
    data["booking"].append({
        "id": i,
        "user_id": random.randint(1, 100),
        "total_price": float(random.randint(50000, 500000)),
        "status": random.choice(["PENDING", "CANCELED", "PAID"]),
        "created_at": random_date(),
        "updated_at": random_date()
    })

# 9. Bảng Ticket
for i in range(1, 101):
    data["ticket"].append({
        "id": i,
        "booking_id": random.randint(1, 100),
        "show_seat_id": random.randint(1, 100),
        "qr_code": fake.sha256()[:20],
        "created_at": random_date(),
        "updated_at": random_date()
    })

# 10. Bảng Payment
for i in range(1, 101):
    data["payment"].append({
        "id": i,
        "booking_id": random.randint(1, 100),
        "payment_method": random.choice(["MOMO", "ZALOPAY", "VNPAY"]),
        "transaction_id": fake.bban(),
        "amount": float(random.randint(50000, 500000)),
        "pay_url": fake.url(),
        "expired_time": random_date(),
        "status": random.choice(["PENDING", "SUCCESSFUL", "FAILED"]),
        "created_at": random_date(),
        "updated_at": random_date()
    })

# 11. Bảng Rules
for i in range(1, 101):
    data["rules"].append({
        "id": i,
        "name": f"Rule {fake.word()}",
        "type": random.choice(["LIMIT", "DISCOUNT"]),
        "value": str(random.randint(5, 50)),
        "active": random.choice([True, False]),
        "user_id": random.randint(1, 100),
        "created_at": random_date(),
        "updated_at": random_date()
    })

# 12. Bảng UserAuthMethod
for i in range(1, 101):
    data["user_auth_method"].append({
        "id": i,
        "user_id": random.randint(1, 100),
        "provider": random.choice(["google", "facebook"]),
        "provider_id": fake.numerify('##########'),
        "refresh_token": fake.sha256(),
        "created_at": random_date(),
        "updated_at": random_date()
    })

# Xuất ra file JSON
with open('cineflow_dummy_data.json', 'w', encoding='utf-8') as f:
    json.dump(data, f, ensure_ascii=False, indent=4)

print("Đã tạo thành công file cineflow_dummy_data.json với 1200 dòng dữ liệu!")