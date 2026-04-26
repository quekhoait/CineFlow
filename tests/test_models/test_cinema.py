import pytest
from sqlalchemy.exc import IntegrityError, DataError, StatementError
from app.models.cinema import Seat, SeatType, Room


class TestCinemaHierarchy:
    def test_seat_foreign_key_constraint(self, test_session):
        invalid_seat = Seat(
            code="A1",
            type=SeatType.SINGLE,
            room_id=999999  #room không tồn tại
        )
        test_session.add(invalid_seat)

        with pytest.raises(IntegrityError):
            test_session.commit()
        test_session.rollback()

    def test_seat_invalid_enum_type(self, test_session, test_setup_cinema_and_room):
        room = test_setup_cinema_and_room
        invalid_seat = Seat(
            code="A2",
            type="INVALID_TYPE",
            room_id=room.id
        )
        test_session.add(invalid_seat)

        with pytest.raises((StatementError, DataError)):
            test_session.commit()
        test_session.rollback()

    def test_successful_cinema_hierarchy(self, test_session, test_setup_cinema_and_room):
        room = test_setup_cinema_and_room
        seat = Seat(code="A3", type=SeatType.COUPLE, room_id=room.id)
        test_session.add(seat)
        test_session.commit()

        saved_room = test_session.get(Room, room.id)
        assert len(saved_room.seats) > 0
        assert saved_room.seats[0].code == "A3"