import datetime
import uuid

from pytest import fixture

from main import app
from app.models.model import SportSession, Location
from app.config.db import session_local
from fastapi.testclient import TestClient

SPORT_SESSIONS_BASE_URL = "/sport-session"


class TestSportSessions:

    @fixture
    def seed_sport_sessions(self):
        active_session = SportSession(
            session_id=uuid.uuid4(),
            user_id=uuid.uuid4(),
            sport_id=uuid.uuid4(),
            duration=100,
            steps=100,
            distance=100,
            calories=100,
            average_speed=100,
            min_heartrate=100,
            max_heartrate=100,
            avg_heartrate=100,
            is_active=True,
            started_at=datetime.datetime.now(),
        )

        finished_session = SportSession(
            session_id=uuid.uuid4(),
            user_id=uuid.uuid4(),
            sport_id=uuid.uuid4(),
            duration=100,
            steps=100,
            distance=100,
            calories=100,
            average_speed=100,
            min_heartrate=100,
            max_heartrate=100,
            avg_heartrate=100,
            is_active=False,
            started_at=datetime.datetime.now(),
        )

        session = session_local()
        session.add(active_session)
        session.add(finished_session)
        session.commit()

        self.active_session_id = active_session.session_id
        self.finished_session_id = finished_session.session_id

        yield

        session = session_local()
        session.query(SportSession).delete()
        session.query(Location).delete()
        session.commit()

    def test_should_create_sport_session(self):
        client = TestClient(app)

        res = client.post(
            f"{SPORT_SESSIONS_BASE_URL}/",
            json={
                "user_id": str(uuid.uuid4()),
                "sport_id": str(uuid.uuid4()),
                "started_at": "2024-04-10T17:55:40.063Z",
                "initial_location": {"latitude": 0.0, "longitude": 0.0, "accuracy": 0.0, "altitude": 0.0, "altitude_accuracy": 0.0, "heading": 0.0, "speed": 0.0},
            },
        )
        json_response = res.json()

        assert res.status_code == 200
        assert "session_id" in json_response
        assert "sport_id" in json_response
        assert "user_id" in json_response
        assert "started_at" in json_response

        self.session_id = json_response["session_id"]

    def test_create_sport_session_should_fail_if_not_the_owner(self):
        client = TestClient(app)

        res = client.post(
            f"{SPORT_SESSIONS_BASE_URL}/",
            json={
                "user_id": str(uuid.uuid4()),
                "sport_id": str(uuid.uuid4()),
                "started_at": "2024-04-10T17:55:40.063Z",
                "initial_location": {"latitude": 0.0, "longitude": 0.0, "accuracy": 0.0, "altitude": 0.0, "altitude_accuracy": 0.0, "heading": 0.0, "speed": 0.0},
            },
            headers={"user-id": str(uuid.uuid4())},
        )
        json_response = res.json()

        assert res.status_code == 403
        assert "error" in json_response

    def test_should_add_location_to_sport_session(self, seed_sport_sessions):
        client = TestClient(app)

        res = client.put(
            f"{SPORT_SESSIONS_BASE_URL}/{self.active_session_id}/location",
            json={"latitude": 0.0, "longitude": 0.0, "accuracy": 0.0, "altitude": 0.0, "altitude_accuracy": 0.0, "heading": 0.0, "speed": 0.0},
        )
        json_response = res.json()

        assert res.status_code == 200
        assert "session_id" in json_response
        assert "latitude" in json_response
        assert "longitude" in json_response
        assert "accuracy" in json_response
        assert "altitude" in json_response
        assert "altitude_accuracy" in json_response
        assert "heading" in json_response
        assert "speed" in json_response

    def test_add_location_to_sport_session_should_fail_if_not_the_owner(self, seed_sport_sessions):
        client = TestClient(app)

        res = client.put(
            f"{SPORT_SESSIONS_BASE_URL}/{self.active_session_id}/location",
            json={"latitude": 0.0, "longitude": 0.0, "accuracy": 0.0, "altitude": 0.0, "altitude_accuracy": 0.0, "heading": 0.0, "speed": 0.0},
            headers={"user-id": str(uuid.uuid4())},
        )
        json_response = res.json()

        assert res.status_code == 403
        assert "error" in json_response

    def test_add_location_to_sport_session_should_fail_if_already_finished(self, seed_sport_sessions):
        client = TestClient(app)

        res = client.put(
            f"{SPORT_SESSIONS_BASE_URL}/{self.finished_session_id}/location",
            json={"latitude": 0.0, "longitude": 0.0, "accuracy": 0.0, "altitude": 0.0, "altitude_accuracy": 0.0, "heading": 0.0, "speed": 0.0},
        )
        json_response = res.json()

        assert res.status_code == 423
        assert "message" in json_response

    def test_add_location_to_sport_session_should_fail_if_not_found(self):
        client = TestClient(app)

        res = client.put(
            f"{SPORT_SESSIONS_BASE_URL}/{uuid.uuid4()}/location",
            json={"latitude": 0.0, "longitude": 0.0, "accuracy": 0.0, "altitude": 0.0, "altitude_accuracy": 0.0, "heading": 0.0, "speed": 0.0},
        )
        json_response = res.json()

        assert res.status_code == 404
        assert "message" in json_response

    def test_should_finish_sport_session(self, seed_sport_sessions):
        client = TestClient(app)

        res = client.patch(
            f"{SPORT_SESSIONS_BASE_URL}/{self.active_session_id}",
            json={"duration": 100, "steps": 100, "distance": 100, "calories": 100, "average_speed": 100, "min_heartrate": 100, "max_heartrate": 100, "avg_heartrate": 100},
        )
        json_response = res.json()

        assert res.status_code == 200
        assert "session_id" in json_response
        assert "sport_id" in json_response
        assert "user_id" in json_response
        assert "started_at" in json_response
        assert "duration" in json_response
        assert "steps" in json_response
        assert "distance" in json_response
        assert "calories" in json_response
        assert "average_speed" in json_response
        assert "min_heartrate" in json_response
        assert "max_heartrate" in json_response
        assert "avg_heartrate" in json_response

    def test_finish_sport_session_should_fail_if_not_the_owner(self, seed_sport_sessions):
        client = TestClient(app)

        res = client.patch(
            f"{SPORT_SESSIONS_BASE_URL}/{self.active_session_id}",
            json={"duration": 100, "steps": 100, "distance": 100, "calories": 100, "average_speed": 100, "min_heartrate": 100, "max_heartrate": 100, "avg_heartrate": 100},
            headers={"user-id": str(uuid.uuid4())},
        )
        json_response = res.json()

        assert res.status_code == 403
        assert "error" in json_response

    def test_finish_sport_session_should_fail_if_already_finished(self, seed_sport_sessions):
        client = TestClient(app)

        res = client.patch(
            f"{SPORT_SESSIONS_BASE_URL}/{self.finished_session_id}",
            json={"duration": 100, "steps": 100, "distance": 100, "calories": 100, "average_speed": 100, "min_heartrate": 100, "max_heartrate": 100, "avg_heartrate": 100},
        )
        json_response = res.json()

        assert res.status_code == 423
        assert "message" in json_response

    def test_finish_sport_session_should_fail_if_not_found(self):
        client = TestClient(app)

        res = client.patch(
            f"{SPORT_SESSIONS_BASE_URL}/{uuid.uuid4()}",
            json={"duration": 100, "steps": 100, "distance": 100, "calories": 100, "average_speed": 100, "min_heartrate": 100, "max_heartrate": 100, "avg_heartrate": 100},
        )
        json_response = res.json()

        assert res.status_code == 404
        assert "message" in json_response

    def test_should_get_sport_session(self, seed_sport_sessions):
        client = TestClient(app)

        res = client.get(f"{SPORT_SESSIONS_BASE_URL}/{self.active_session_id}")
        json_response = res.json()

        assert res.status_code == 200
        assert "session_id" in json_response
        assert "sport_id" in json_response
        assert "user_id" in json_response
        assert "started_at" in json_response
        assert "duration" in json_response
        assert "steps" in json_response
        assert "distance" in json_response
        assert "calories" in json_response
        assert "average_speed" in json_response
        assert "min_heartrate" in json_response
        assert "max_heartrate" in json_response
        assert "avg_heartrate" in json_response

    def test_get_sport_session_should_fail_if_not_the_owner(self, seed_sport_sessions):
        client = TestClient(app)

        res = client.get(f"{SPORT_SESSIONS_BASE_URL}/{self.active_session_id}", headers={"user-id": str(uuid.uuid4())})
        json_response = res.json()

        assert res.status_code == 403
        assert "error" in json_response

    def test_get_sport_session_should_fail_if_not_found(self):
        client = TestClient(app)

        res = client.get(f"{SPORT_SESSIONS_BASE_URL}/{uuid.uuid4()}")
        json_response = res.json()

        assert res.status_code == 404
        assert "message" in json_response

    def test_get_spot_sessions(self, seed_sport_sessions):
        client = TestClient(app)
        user_id = uuid.uuid4()

        session_1 = SportSession(
            session_id=uuid.uuid4(),
            user_id=user_id,
            sport_id=uuid.uuid4(),
            duration=100,
            steps=100,
            distance=100,
            calories=100,
            average_speed=100,
            min_heartrate=100,
            max_heartrate=100,
            avg_heartrate=100,
            is_active=True,
            started_at=datetime.datetime.now(),
        )

        session_2 = SportSession(
            session_id=uuid.uuid4(),
            user_id=user_id,
            sport_id=uuid.uuid4(),
            duration=100,
            steps=100,
            distance=100,
            calories=100,
            average_speed=100,
            min_heartrate=100,
            max_heartrate=100,
            avg_heartrate=100,
            is_active=False,
            started_at=datetime.datetime.now(),
        )

        session = session_local()
        session.add(session_1)
        session.add(session_2)
        session.commit()

        res = client.get(f"{SPORT_SESSIONS_BASE_URL}/", headers={"user-id": str(user_id)})
        json_response = res.json()

        assert res.status_code == 200
        assert len(json_response) == 2

    def test_get_spot_sessions_should_should_only_return_users_sessions(self, seed_sport_sessions):
        client = TestClient(app)
        user_id = uuid.uuid4()

        session_1 = SportSession(
            session_id=uuid.uuid4(),
            user_id=user_id,
            sport_id=uuid.uuid4(),
            duration=100,
            steps=100,
            distance=100,
            calories=100,
            average_speed=100,
            min_heartrate=100,
            max_heartrate=100,
            avg_heartrate=100,
            is_active=True,
            started_at=datetime.datetime.now(),
        )

        session_2 = SportSession(
            session_id=uuid.uuid4(),
            user_id=uuid.uuid4(),
            sport_id=uuid.uuid4(),
            duration=100,
            steps=100,
            distance=100,
            calories=100,
            average_speed=100,
            min_heartrate=100,
            max_heartrate=100,
            avg_heartrate=100,
            is_active=True,
            started_at=datetime.datetime.now(),
        )

        session = session_local()
        session.add(session_1)
        session.add(session_2)
        session.commit()

        res = client.get(f"{SPORT_SESSIONS_BASE_URL}/", headers={"user-id": str(user_id)})
        json_response = res.json()

        assert res.status_code == 200
        assert len(json_response) == 1

    def test_get_active_sport_sessions(self, seed_sport_sessions):
        client = TestClient(app)
        user_id = uuid.uuid4()
        user_2_id = uuid.uuid4()
        user_3_id = uuid.uuid4()

        current_time = datetime.datetime.now()

        session_1 = SportSession(
            session_id=uuid.uuid4(),
            user_id=user_id,
            sport_id=uuid.uuid4(),
            duration=100,
            steps=100,
            distance=100,
            calories=100,
            average_speed=100,
            min_heartrate=100,
            max_heartrate=100,
            avg_heartrate=100,
            is_active=True,
            started_at=datetime.datetime.now(),
        )

        location_1_session_1 = Location(
            session_id=session_1.session_id,
            latitude=0.0,
            longitude=0.0,
            accuracy=0.0,
            altitude=0.0,
            altitude_accuracy=0.0,
            heading=0.0,
            speed=0.0,
            created_at=current_time,
        )

        location_2_session_1 = Location(
            session_id=session_1.session_id,
            latitude=0.0,
            longitude=0.0,
            accuracy=0.0,
            altitude=0.0,
            altitude_accuracy=0.0,
            heading=0.0,
            speed=0.0,
            created_at=current_time + datetime.timedelta(seconds=10),
        )

        session_2 = SportSession(
            session_id=uuid.uuid4(),
            user_id=user_2_id,
            sport_id=uuid.uuid4(),
            duration=100,
            steps=100,
            distance=100,
            calories=100,
            average_speed=100,
            min_heartrate=100,
            max_heartrate=100,
            avg_heartrate=100,
            is_active=True,
            started_at=datetime.datetime.now(),
        )

        location_1_session_2 = Location(
            session_id=session_2.session_id,
            latitude=0.0,
            longitude=0.0,
            accuracy=0.0,
            altitude=0.0,
            altitude_accuracy=0.0,
            heading=0.0,
            speed=0.0,
            created_at=current_time,
        )

        location_2_session_2 = Location(
            session_id=session_2.session_id,
            latitude=0.0,
            longitude=0.0,
            accuracy=0.0,
            altitude=0.0,
            altitude_accuracy=0.0,
            heading=0.0,
            speed=0.0,
            created_at=current_time - datetime.timedelta(seconds=10),
        )

        session_3 = SportSession(
            session_id=uuid.uuid4(),
            user_id=user_3_id,
            sport_id=uuid.uuid4(),
            duration=100,
            steps=100,
            distance=100,
            calories=100,
            average_speed=100,
            min_heartrate=100,
            max_heartrate=100,
            avg_heartrate=100,
            is_active=False,
            started_at=datetime.datetime.now(),
        )

        session = session_local()
        session.add(session_1)
        session.add(session_2)
        session.add(session_3)
        session.add(location_1_session_1)
        session.add(location_2_session_1)
        session.add(location_1_session_2)
        session.add(location_2_session_2)
        session.commit()

        res = client.get(f"{SPORT_SESSIONS_BASE_URL}/active-sport-sessions", headers={"x-api-key": "secret"})
        json_response = res.json()

        print(json_response)
        assert res.status_code == 200
        assert len(json_response) == 2
        assert json_response[0]["user_id"] == str(session_1.user_id)
        assert json_response[0]["latitude"] == location_2_session_1.latitude
        assert json_response[0]["longitude"] == location_2_session_1.longitude
        assert json_response[1]["user_id"] == str(session_2.user_id)
        assert json_response[1]["latitude"] == location_1_session_2.latitude
        assert json_response[1]["longitude"] == location_1_session_2.longitude
