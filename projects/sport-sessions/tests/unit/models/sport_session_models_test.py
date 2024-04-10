import uuid

from app.models.model import SportSession, Location


class TestSportSessionModel:
    def test_create_sport_session(self):
        sport_session_dict = {
            "session_id": uuid.uuid4(),
            "user_id": uuid.uuid4(),
            "sport_id": uuid.uuid4(),
            "duration": 10,
            "steps": 100,
            "distance": 1000,
            "calories": 1000,
            "average_speed": 10,
            "min_heartrate": 50,
            "max_heartrate": 150,
            "avg_heartrate": 100,
            "is_active": True,
            "started_at": "2021-08-01T00:00:00",
        }
        sport_session = SportSession(**sport_session_dict)

        assert sport_session.session_id == sport_session_dict["session_id"]
        assert sport_session.user_id == sport_session_dict["user_id"]
        assert sport_session.sport_id == sport_session_dict["sport_id"]
        assert sport_session.duration == sport_session_dict["duration"]
        assert sport_session.steps == sport_session_dict["steps"]
        assert sport_session.distance == sport_session_dict["distance"]
        assert sport_session.calories == sport_session_dict["calories"]
        assert sport_session.average_speed == sport_session_dict["average_speed"]
        assert sport_session.min_heartrate == sport_session_dict["min_heartrate"]
        assert sport_session.max_heartrate == sport_session_dict["max_heartrate"]
        assert sport_session.avg_heartrate == sport_session_dict["avg_heartrate"]
        assert sport_session.is_active == sport_session_dict["is_active"]
        assert sport_session.started_at == sport_session_dict["started_at"]

    def test_create_location(self):
        location_dict = {
            "location_id": uuid.uuid4(),
            "session_id": uuid.uuid4(),
            "latitude": 10.0,
            "longitude": 20.0,
            "accuracy": 10.0,
            "altitude": 10.0,
            "altitude_accuracy": 10.0,
            "heading": 10.0,
            "speed": 10.0,
        }
        location = Location(**location_dict)

        assert location.location_id == location_dict["location_id"]
        assert location.session_id == location_dict["session_id"]
        assert location.latitude == location_dict["latitude"]
        assert location.longitude == location_dict["longitude"]
        assert location.accuracy == location_dict["accuracy"]
        assert location.altitude == location_dict["altitude"]
        assert location.altitude_accuracy == location_dict["altitude_accuracy"]
        assert location.heading == location_dict["heading"]
        assert location.speed == location_dict["speed"]
