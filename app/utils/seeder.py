from datetime import datetime, date, timedelta
from werkzeug.security import generate_password_hash
from app import db, models


def run_seeding():
    print("--- Starting CineFlow Data Seeding ---")

    print("1. Dropping and recreating Database...")
    db.drop_all()
    db.create_all()

    print('2. Creating Admin account...')
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

    print("3. Configuring Rules...")
    rules_data = [
        ("SINGLE_WEEKDAY", "VND", "50000", True),
        ("SINGLE_WEEKEND", "VND", "65000", True),
        ("COUPLE_WEEKDAY", "VND", "100000", True),
        ("COUPLE_WEEKEND", "VND", "125000", True),
        ("CANCEL_HOUR", "HOUR", "2", True),
        ("HOLD_BOOKING", "MINUTES", "10", True),
    ]
    for name, r_type, value, active in rules_data:
        rule = models.Rules(name=name, type=r_type, value=value, active=active, user_id=admin.id)
        db.session.add(rule)

    print("4. Initializing 20 films (10 Now Showing & 10 Upcoming)...")

    now_showing_films = [
        models.Film(title='Fantastic Four: First Steps', description='Gia đình siêu anh hùng đầu tiên của Marvel.',
                    genre='Action, Sci-Fi', age_limit=13, release_date=date(2026, 5, 1), expired_date=date(2026, 7, 30),
                    poster='https://encrypted-tbn3.gstatic.com/images?q=tbn:ANd9GcQd-BN3XSYs1IEmKerLM_hwcEKoJL25llBJmsAoWgTMXo3PHCCe', duration=130),
        models.Film(title='Lật Mặt 8: Vòng Xoáy', description='Bom tấn hành động Lý Hải.', genre='Action, Drama',
                    age_limit=16, release_date=date(2026, 4, 26), expired_date=date(2026, 6, 26),
                    poster='https://cinema.momocdn.net/img/77210013985876184-lm81.png?size=M', duration=125),
        models.Film(title='Godzilla x Kong: The New Empire Sequel', description='Hai Titan huyền thoại tái hợp.',
                    genre='Action, Sci-Fi', age_limit=13, release_date=date(2026, 3, 20),
                    expired_date=date(2026, 5, 20),
                    poster='https://encrypted-tbn0.gstatic.com/images?q=tbn:ANd9GcShQcL8k9ZNqTPP-vyiMwvfa8j6SF3bUc-thL0t4OBfO8ZDeg0d', duration=115),
        models.Film(title='Fast X: Part 2', description='Chương cuối của gia đình Toretto.', genre='Action, Crime',
                    age_limit=16, release_date=date(2026, 4, 3), expired_date=date(2026, 6, 3),
                    poster='https://upload.wikimedia.org/wikipedia/vi/2/22/Fast_X_VN_poster.jpg', duration=140),
        models.Film(title='The Super Mario Bros. Movie 2', description='Hành trình mới của anh em Mario.',
                    genre='Animation, Adventure', age_limit=0, release_date=date(2026, 4, 10),
                    expired_date=date(2026, 6, 15),
                    poster='https://encrypted-tbn2.gstatic.com/images?q=tbn:ANd9GcSbQAer_UacWJzfW1n8AREzPD6-MRfyAZT5aBEIhVYZqo0mclfO', duration=100),
        models.Film(title='Five Nights at Freddy\'s 2', description='Cơn ác mộng kinh hoàng trở lại.',
                    genre='Horror, Thriller', age_limit=18, release_date=date(2026, 4, 15),
                    expired_date=date(2026, 6, 10),
                    poster='https://cdn1.epicgames.com/spt-assets/5c65df08b03a43eb8be026116ef8e979/five-nights-at-freddys-into-the-pit-161gk.png', duration=110),
        models.Film(title='Mortal Kombat 2', description='Giải đấu sinh tử bắt đầu.', genre='Action, Fantasy',
                    age_limit=18, release_date=date(2026, 4, 24), expired_date=date(2026, 6, 25),
                    poster='https://upload.wikimedia.org/wikipedia/en/thumb/9/9a/Mortal_Kombat_II_%28film%29_poster.jpg/250px-Mortal_Kombat_II_%28film%29_poster.jpg', duration=120),
        models.Film(title='Kung Fu Panda 5', description='Gấu Po du hành vùng đất mới.', genre='Animation, Comedy',
                    age_limit=0, release_date=date(2026, 3, 5), expired_date=date(2026, 5, 15),
                    poster='https://cdn.moveek.com/storage/media/cache/tall/r6TxoNG69V.jpg', duration=95),
        models.Film(title='A Quiet Place: Day Two', description='Sống sót trong im lặng.', genre='Horror, Sci-Fi',
                    age_limit=16, release_date=date(2026, 4, 18), expired_date=date(2026, 6, 18),
                    poster='https://encrypted-tbn0.gstatic.com/images?q=tbn:ANd9GcQt7r7G9_OrP8w07k0rNVuvq-PSx47lUoV2VQ&s', duration=105),
        models.Film(title='John Wick: Chapter 5', description='Sát thủ John Wick trở lại.', genre='Action, Thriller',
                    age_limit=18, release_date=date(2026, 3, 27), expired_date=date(2026, 5, 30),
                    poster='https://encrypted-tbn0.gstatic.com/images?q=tbn:ANd9GcTYeBgUCM4wI8mP183zu9Me1cPLZbn8lpsBbQ&s', duration=160)
    ]

    upcoming_films = [
        models.Film(title='The Mandalorian & Grogu', description='Star Wars hits the big screen.',
                    genre='Action, Sci-Fi',
                    age_limit=13, release_date=date(2026, 5, 22), expired_date=date(2026, 8, 30),
                    poster='https://m.media-amazon.com/images/M/MV5BYzVkMmJhNTgtNjYwOS00YjM0LThlNWEtNGExNmIxZjVkMmJhXkEyXkFqcGc@._V1_.jpg',
                    duration=125),
        models.Film(title='Jurassic World: Rebirth', description='A new era of dinosaurs begins.',
                    genre='Action, Sci-Fi',
                    age_limit=13, release_date=date(2026, 7, 2), expired_date=date(2026, 9, 20),
                    poster='https://m.media-amazon.com/images/M/MV5BNjg2NTcwYWQtYzk4NS00MTJhLWEzZjItMzIxNjk3YzlkYzU0XkEyXkFqcGc@._V1_FMjpg_UX1000_.jpg',
                    duration=135),
        models.Film(title='Shrek 5', description='The ogre and the donkey are back.', genre='Animation, Comedy',
                    age_limit=0,
                    release_date=date(2026, 7, 1), expired_date=date(2026, 9, 30),
                    poster='https://m.media-amazon.com/images/M/MV5BNmNkNmRkNDAtOTMzNC00MWYzLWJhNjMtYjNkZTNjODVhOTg2XkEyXkFqcGc@._V1_FMjpg_UX1000_.jpg',
                    duration=92),
        models.Film(title='Teenage Mutant Ninja Turtles 2', description='Turtles vs the Foot Clan.',
                    genre='Animation, Action', age_limit=13, release_date=date(2026, 8, 7),
                    expired_date=date(2026, 10, 31),
                    poster='https://upload.wikimedia.org/wikipedia/en/6/6c/Teenage_Mutant_Ninja_Turtles_II_%281991_film%29_poster.jpg',
                    duration=102),
        models.Film(title='Tron: Ares', description='The digital world enters reality.', genre='Sci-Fi, Action',
                    age_limit=13,
                    release_date=date(2026, 10, 10), expired_date=date(2026, 12, 31),
                    poster='https://lumiere-a.akamaihd.net/v1/images/p_disneymovies_tronares_poster_nowstreaming_1f6b491f.jpeg',
                    duration=120),
        models.Film(title='Frozen III', description='Elsa and Anna\'s new magical journey.', genre='Animation, Family',
                    age_limit=0, release_date=date(2026, 11, 25), expired_date=date(2027, 2, 28),
                    poster='https://encrypted-tbn0.gstatic.com/images?q=tbn:ANd9GcQgsuZA9-Dp4oixpSLwrdRv0EV7ruI9MtFdZg&s', duration=105),
        models.Film(title='The Hunger Games: Sunrise', description='The 50th Games story.', genre='Action, Drama',
                    age_limit=16, release_date=date(2026, 11, 20), expired_date=date(2027, 2, 20),
                    poster='https://upload.wikimedia.org/wikipedia/en/2/20/Sunrise_on_the_Reaping_book_cover.jpg',
                    duration=145),
        models.Film(title='Star Wars: New Jedi Order', description='Rey Skywalker builds the future.',
                    genre='Action, Sci-Fi', age_limit=13, release_date=date(2026, 12, 18),
                    expired_date=date(2027, 3, 30),
                    poster='https://encrypted-tbn0.gstatic.com/images?q=tbn:ANd9GcRFXJzW4ZHKruTR_d2zTDQDk3JsB2PcPPOh1Q&s', duration=150),
        models.Film(title='Lord of the Rings: Gollum', description='The journey to find the precious.',
                    genre='Fantasy, Adventure',
                    age_limit=13, release_date=date(2026, 12, 24), expired_date=date(2027, 3, 15),
                    poster='https://upload.wikimedia.org/wikipedia/en/thumb/2/23/The_Lord_of_the_Rings_Gollum.jpg/250px-The_Lord_of_the_Rings_Gollum.jpg',
                    duration=165),
        models.Film(title='Kraven the Hunter', description='Marvel\'s greatest hunter on the hunt.',
                    genre='Action, Sci-Fi',
                    age_limit=16, release_date=date(2026, 12, 11), expired_date=date(2027, 2, 15),
                    poster='https://upload.wikimedia.org/wikipedia/en/e/ec/Kraven_the_Hunter_%28film%29_poster.jpg',
                    duration=115)
    ]

    films_data = now_showing_films + upcoming_films
    db.session.add_all(films_data)
    db.session.commit()

    films_data = now_showing_films + upcoming_films
    db.session.add_all(films_data)
    db.session.commit()

    print("5. Creating Cinemas, Rooms, and Seats...")
    cinemas_info = [
        {'name': 'CineFlow Hà Nội', 'city': 'Hà Nội', 'films': [0, 1, 2, 3, 4]},
        {'name': 'CineFlow Đà Nẵng', 'city': 'Đà Nẵng', 'films': [5, 6, 7]},
        {'name': 'CineFlow Hồ Chí Minh', 'city': 'Hồ Chí Minh', 'films': [8, 9, 0]}
    ]

    for info in cinemas_info:
        cinema = models.Cinema(name=info['name'], province=info['city'], address="Số 1 Đường ABC", hotline="19001000")
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
                        seat = models.Seat(
                            code=f"C{cinema.id}R{room.id}-{row_char}{col}",
                            type=models.SeatType.COUPLE, row=row_char, column=col, room_id=room.id
                        )
                        db.session.add(seat)
                else:
                    for col in range(1, 13):
                        if col in [4, 9]: continue
                        seat = models.Seat(
                            code=f"C{cinema.id}R{room.id}-{row_char}{col}",
                            type=models.SeatType.SINGLE, row=row_char, column=col, room_id=room.id
                        )
                        db.session.add(seat)
            db.session.commit()

        print(f"   -> Creating ~30 shows/day for films at {cinema.name}...")
        today = datetime.now()
        base_time_slots = [
            (8, 0), (9, 45), (11, 30), (13, 15), (15, 0),
            (16, 45), (18, 30), (20, 15), (22, 0), (23, 30)
        ]

        rooms = models.Room.query.filter_by(cinema_id=cinema.id).all()
        for f_idx in info['films']:
            film = films_data[f_idx]

            for day_offset in range(3):
                show_date = today + timedelta(days=day_offset)

                for room_idx, room in enumerate(rooms):
                    for hour, minute in base_time_slots:
                        offset_minutes = room_idx * 15
                        total_minutes = minute + offset_minutes
                        final_hour = hour + (total_minutes // 60)
                        final_minute = total_minutes % 60

                        if final_hour > 23: continue

                        show = models.Show(
                            start_time=show_date.replace(hour=final_hour, minute=final_minute, second=0, microsecond=0),
                            film_id=film.id,
                            room_id=room.id
                        )
                        db.session.add(show)
        db.session.commit()

    print("--- Seeding Complete! CineFlow system is ready. ---")


if __name__ == '__main__':
    run_seeding()