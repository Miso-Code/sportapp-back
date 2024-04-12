import uuid

import pytest
from unittest.mock import patch, MagicMock
from sqlalchemy.orm import Session

from app.exceptions.exceptions import NotFoundError, NotActiveError
from app.models.model import SportSession
from app.services.sport_sessions import SportSessionService
from app.services.sport_sessions import SportSessionStart, SportSessionLocationCreate, SportSessionFinish


class TestSportSessionService:
    def test_start_sport_session_should_create_sport_session(self, mocked_db_session: Session) -> None:
        # Given
        sport_service = SportSessionService(mocked_db_session)
        sport_session_start = SportSessionStart(
            sport_id=uuid.uuid4(),
            user_id=uuid.uuid4(),
            started_at="2022-01-01T00:00:00",
            initial_location={"latitude": 10.0, "longitude": 20.0, "accuracy": 10.0, "altitude": 10.0, "altitude_accuracy": 10.0, "heading": 10.0, "speed": 10.0},
        )

        # When
        sport_session = sport_service.start_sport_session(sport_session_start)

        # Then
        assert sport_session["sport_id"] == str(sport_session_start.sport_id)
        assert sport_session["user_id"] == str(sport_session_start.user_id)
        assert sport_session["started_at"] == sport_session_start.started_at.isoformat()

    def test_add_location_to_sport_session_should_create_location(self, mocked_db_session: Session) -> None:
        # Given
        sport_session_id = uuid.uuid4()
        mocked_db_session.add(SportSession(session_id=sport_session_id, sport_id=uuid.uuid4(), user_id=uuid.uuid4(), started_at="2022-01-01T00:00:00", is_active=True))

        sport_service = SportSessionService(mocked_db_session)

        location = SportSessionLocationCreate(latitude=10.0, longitude=20.0, accuracy=10.0, altitude=10.0, altitude_accuracy=10.0, heading=10.0, speed=10.0)

        # When
        sport_session = sport_service.add_location_to_sport_session(sport_session_id, location)

        # Then
        assert sport_session["session_id"] == str(sport_session_id)
        assert sport_session["latitude"] == location.latitude
        assert sport_session["longitude"] == location.longitude
        assert sport_session["accuracy"] == location.accuracy
        assert sport_session["altitude"] == location.altitude
        assert sport_session["altitude_accuracy"] == location.altitude_accuracy
        assert sport_session["heading"] == location.heading
        assert sport_session["speed"] == location.speed

    def test_add_location_to_sport_session_should_raise_not_found_error(self, mocked_db_session: Session) -> None:
        # Given
        sport_service = SportSessionService(mocked_db_session)
        sport_session_id = uuid.uuid4()
        location = SportSessionLocationCreate(latitude=10.0, longitude=20.0, accuracy=10.0, altitude=10.0, altitude_accuracy=10.0, heading=10.0, speed=10.0)

        # When
        with pytest.raises(NotFoundError):
            sport_service.add_location_to_sport_session(sport_session_id, location)

    def test_add_location_to_sport_session_should_raise_not_active_error(self, mocked_db_session: Session) -> None:
        # Given
        sport_session_id = uuid.uuid4()
        mocked_db_session.add(SportSession(session_id=sport_session_id, sport_id=uuid.uuid4(), user_id=uuid.uuid4(), started_at="2022-01-01T00:00:00", is_active=False))

        sport_service = SportSessionService(mocked_db_session)
        location = SportSessionLocationCreate(latitude=10.0, longitude=20.0, accuracy=10.0, altitude=10.0, altitude_accuracy=10.0, heading=10.0, speed=10.0)

        # When
        with pytest.raises(NotActiveError):
            sport_service.add_location_to_sport_session(sport_session_id, location)

    def test_finish_sport_session_should_return_metrics(self, mocked_db_session: Session) -> None:
        # Given
        sport_session_id = uuid.uuid4()
        mocked_db_session.add(SportSession(session_id=sport_session_id, sport_id=uuid.uuid4(), user_id=uuid.uuid4(), started_at="2022-01-01T00:00:00", is_active=True))

        sport_service = SportSessionService(mocked_db_session)

        sport_session_finish = SportSessionFinish(
            duration=5,
            steps=1000,
            distance=1000,
            calories=1000,
            average_speed=1000,
            min_heartrate=1000,
            max_heartrate=1000,
            avg_heartrate=1000,
        )

        # When
        sport_session = sport_service.finish_sport_session(sport_session_id, sport_session_finish)

        # Then
        assert sport_session["session_id"] == str(sport_session_id)
        assert sport_session["duration"] == sport_session_finish.duration
        assert sport_session["distance"] == sport_session_finish.distance
        assert sport_session["calories"] == sport_session_finish.calories
        assert sport_session["average_speed"] == sport_session_finish.average_speed
        assert sport_session["min_heartrate"] == sport_session_finish.min_heartrate
        assert sport_session["max_heartrate"] == sport_session_finish.max_heartrate
        assert sport_session["avg_heartrate"] == sport_session_finish.avg_heartrate

    def test_finish_sport_session_should_raise_not_found_error(self, mocked_db_session: Session) -> None:
        # Given
        sport_service = SportSessionService(mocked_db_session)
        sport_session_id = uuid.uuid4()
        sport_session_finish = SportSessionFinish(
            duration=5,
            steps=1000,
            distance=1000,
            calories=1000,
            average_speed=1000,
            min_heartrate=1000,
            max_heartrate=1000,
            avg_heartrate=1000,
        )

        # When
        with pytest.raises(NotFoundError):
            sport_service.finish_sport_session(sport_session_id, sport_session_finish)

    def test_finish_sport_session_should_raise_not_active_error(self, mocked_db_session: Session) -> None:
        # Given
        sport_session_id = uuid.uuid4()
        mocked_db_session.add(SportSession(session_id=sport_session_id, sport_id=uuid.uuid4(), user_id=uuid.uuid4(), started_at="2022-01-01T00:00:00", is_active=False))

        sport_service = SportSessionService(mocked_db_session)
        sport_session_finish = SportSessionFinish(
            duration=5,
            steps=1000,
            distance=1000,
            calories=1000,
            average_speed=1000,
            min_heartrate=1000,
            max_heartrate=1000,
            avg_heartrate=1000,
        )

        # When
        with pytest.raises(NotActiveError):
            sport_service.finish_sport_session(sport_session_id, sport_session_finish)

    @patch("app.services.sport_sessions.estimate_distance", return_value=1234)
    def test_finish_sport_session_should_calculate_distance(self, mocked_db_session: Session) -> None:
        # Given
        sport_session_id = uuid.uuid4()
        mocked_db_session.add(SportSession(session_id=sport_session_id, sport_id=uuid.uuid4(), user_id=uuid.uuid4(), started_at="2022-01-01T00:00:00", is_active=True))

        sport_service = SportSessionService(mocked_db_session)

        sport_session_finish = SportSessionFinish(
            duration=5,
            steps=1000,
            distance=None,
            calories=1000,
            average_speed=1000,
            min_heartrate=1000,
            max_heartrate=1000,
            avg_heartrate=1000,
        )

        # When
        sport_session = sport_service.finish_sport_session(sport_session_id, sport_session_finish)

        # Then
        assert sport_session["distance"] == 1234

    @patch("app.services.sport_sessions.estimate_calories_burned", return_value=1234)
    def test_finish_sport_session_should_calculate_calories(self, mocked_db_session: Session) -> None:
        # Given
        sport_session_id = uuid.uuid4()
        mocked_db_session.add(SportSession(session_id=sport_session_id, sport_id=uuid.uuid4(), user_id=uuid.uuid4(), started_at="2022-01-01T00:00:00", is_active=True))

        sport_service = SportSessionService(mocked_db_session)

        sport_session_finish = SportSessionFinish(
            duration=5,
            steps=1000,
            distance=1000,
            calories=None,
            average_speed=1000,
            min_heartrate=1000,
            max_heartrate=1000,
            avg_heartrate=1000,
        )

        # When
        sport_session = sport_service.finish_sport_session(sport_session_id, sport_session_finish)

        # Then
        assert sport_session["calories"] == 1234

    @patch("app.services.sport_sessions.estimate_speed", return_value=1234)
    def test_finish_sport_session_should_calculate_speed(self, mocked_db_session: Session) -> None:
        # Given
        sport_session_id = uuid.uuid4()
        mocked_db_session.add(SportSession(session_id=sport_session_id, sport_id=uuid.uuid4(), user_id=uuid.uuid4(), started_at="2022-01-01T00:00:00", is_active=True))

        sport_service = SportSessionService(mocked_db_session)

        sport_session_finish = SportSessionFinish(
            duration=5,
            steps=1000,
            distance=1000,
            calories=1000,
            average_speed=None,
            min_heartrate=1000,
            max_heartrate=1000,
            avg_heartrate=1000,
        )

        # When
        sport_session = sport_service.finish_sport_session(sport_session_id, sport_session_finish)

        # Then
        assert sport_session["average_speed"] == 1234

    def test_get_sport_session_should_return_sport_session(self, mocked_db_session: Session) -> None:
        # Given
        sport_session_id = uuid.uuid4()
        mocked_db_session.add(SportSession(session_id=sport_session_id, sport_id=uuid.uuid4(), user_id=uuid.uuid4(), started_at="2022-01-01T00:00:00", is_active=True))

        sport_service = SportSessionService(mocked_db_session)

        # When
        sport_session = sport_service.get_sport_session(sport_session_id)

        # Then
        assert sport_session["session_id"] == str(sport_session_id)

    def test_get_sport_session_should_raise_not_found_error(self, mocked_db_session: Session) -> None:
        # Given
        sport_service = SportSessionService(mocked_db_session)
        sport_session_id = uuid.uuid4()

        # When
        with pytest.raises(NotFoundError):
            sport_service.get_sport_session(sport_session_id)

    def test_get_sport_sessions_should_return_sport_sessions(self, mocked_db_session: Session) -> None:
        # Given
        user_id = uuid.uuid4()
        mocked_db_session.add(SportSession(session_id=uuid.uuid4(), sport_id=uuid.uuid4(), user_id=user_id, started_at="2022-01-01T00:00:00", is_active=True))
        mocked_db_session.add(SportSession(session_id=uuid.uuid4(), sport_id=uuid.uuid4(), user_id=user_id, started_at="2022-01-01T00:00:00", is_active=True))

        sport_service = SportSessionService(mocked_db_session)

        # When
        sport_sessions = sport_service.get_sport_sessions(user_id)

        # Then
        assert len(sport_sessions) == 2

    def test_get_sport_sessions_should_only_return_users_sessions(self) -> None:
        # Given
        user_id = uuid.uuid4()
        db_mock = MagicMock(spec=Session)
        sport_service = SportSessionService(db_mock)

        db_mock.query.filter.first.return_value = []

        # When
        sport_sessions = sport_service.get_sport_sessions(user_id)

        # Then
        assert len(sport_sessions) == 0
