import datetime
import uuid

from pytest import fixture

from main import app
from app.models.model import SportSession
from app.config.db import session_local
from fastapi.testclient import TestClient


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

    def test_should_create_sport_session(self):
        client = TestClient(app)

        res = client.post(
            "/sport-session/",
            json={
                "user_id": str(uuid.uuid4()),
                "sport_id": str(uuid.uuid4()),
                "started_at": "2024-04-10T17:55:40.063Z",
                "initial_location": {"latitude": 0.0, "longitude": 0.0, "accuracy": 0.0, "altitude": 0.0, "altitude_accuracy": 0.0, "heading": 0.0, "speed": 0.0},
            },
        )

        assert res.status_code == 200
        assert "session_id" in res.json()
        assert "sport_id" in res.json()
        assert "user_id" in res.json()
        assert "started_at" in res.json()

        self.session_id = res.json()["session_id"]

    def test_create_sport_session_should_fail_if_not_the_owner(self):
        client = TestClient(app)

        res = client.post(
            "/sport-session/",
            json={
                "user_id": str(uuid.uuid4()),
                "sport_id": str(uuid.uuid4()),
                "started_at": "2024-04-10T17:55:40.063Z",
                "initial_location": {"latitude": 0.0, "longitude": 0.0, "accuracy": 0.0, "altitude": 0.0, "altitude_accuracy": 0.0, "heading": 0.0, "speed": 0.0},
            },
            headers={"user-id": str(uuid.uuid4())},
        )

        assert res.status_code == 403
        assert "error" in res.json()

    def test_should_add_location_to_sport_session(self, seed_sport_sessions):
        client = TestClient(app)

        res = client.put(
            f"/sport-session/{self.active_session_id}/location",
            json={"latitude": 0.0, "longitude": 0.0, "accuracy": 0.0, "altitude": 0.0, "altitude_accuracy": 0.0, "heading": 0.0, "speed": 0.0},
        )

        assert res.status_code == 200
        assert "session_id" in res.json()
        assert "latitude" in res.json()
        assert "longitude" in res.json()
        assert "accuracy" in res.json()
        assert "altitude" in res.json()
        assert "altitude_accuracy" in res.json()
        assert "heading" in res.json()
        assert "speed" in res.json()

    def test_add_location_to_sport_session_should_fail_if_not_the_owner(self, seed_sport_sessions):
        client = TestClient(app)

        res = client.put(
            f"/sport-session/{self.active_session_id}/location",
            json={"latitude": 0.0, "longitude": 0.0, "accuracy": 0.0, "altitude": 0.0, "altitude_accuracy": 0.0, "heading": 0.0, "speed": 0.0},
            headers={"user-id": str(uuid.uuid4())},
        )

        assert res.status_code == 403
        assert "error" in res.json()

    def test_add_location_to_sport_session_should_fail_if_already_finished(self, seed_sport_sessions):
        client = TestClient(app)

        res = client.put(
            f"/sport-session/{self.finished_session_id}/location",
            json={"latitude": 0.0, "longitude": 0.0, "accuracy": 0.0, "altitude": 0.0, "altitude_accuracy": 0.0, "heading": 0.0, "speed": 0.0},
        )

        assert res.status_code == 423
        assert "message" in res.json()

    def test_add_location_to_sport_session_should_fail_if_not_found(self):
        client = TestClient(app)

        res = client.put(
            f"/sport-session/{uuid.uuid4()}/location",
            json={"latitude": 0.0, "longitude": 0.0, "accuracy": 0.0, "altitude": 0.0, "altitude_accuracy": 0.0, "heading": 0.0, "speed": 0.0},
        )

        assert res.status_code == 404
        assert "message" in res.json()

    def test_should_finish_sport_session(self, seed_sport_sessions):
        client = TestClient(app)

        res = client.patch(
            f"/sport-session/{self.active_session_id}",
            json={"duration": 100, "steps": 100, "distance": 100, "calories": 100, "average_speed": 100, "min_heartrate": 100, "max_heartrate": 100, "avg_heartrate": 100},
        )

        assert res.status_code == 200
        assert "session_id" in res.json()
        assert "sport_id" in res.json()
        assert "user_id" in res.json()
        assert "started_at" in res.json()
        assert "duration" in res.json()
        assert "steps" in res.json()
        assert "distance" in res.json()
        assert "calories" in res.json()
        assert "average_speed" in res.json()
        assert "min_heartrate" in res.json()
        assert "max_heartrate" in res.json()
        assert "avg_heartrate" in res.json()

    def test_finish_sport_session_should_fail_if_not_the_owner(self, seed_sport_sessions):
        client = TestClient(app)

        res = client.patch(
            f"/sport-session/{self.active_session_id}",
            json={"duration": 100, "steps": 100, "distance": 100, "calories": 100, "average_speed": 100, "min_heartrate": 100, "max_heartrate": 100, "avg_heartrate": 100},
            headers={"user-id": str(uuid.uuid4())},
        )

        assert res.status_code == 403
        assert "error" in res.json()

    def test_finish_sport_session_should_fail_if_already_finished(self, seed_sport_sessions):
        client = TestClient(app)

        res = client.patch(
            f"/sport-session/{self.finished_session_id}",
            json={"duration": 100, "steps": 100, "distance": 100, "calories": 100, "average_speed": 100, "min_heartrate": 100, "max_heartrate": 100, "avg_heartrate": 100},
        )

        assert res.status_code == 423
        assert "message" in res.json()

    def test_finish_sport_session_should_fail_if_not_found(self):
        client = TestClient(app)

        res = client.patch(
            f"/sport-session/{uuid.uuid4()}",
            json={"duration": 100, "steps": 100, "distance": 100, "calories": 100, "average_speed": 100, "min_heartrate": 100, "max_heartrate": 100, "avg_heartrate": 100},
        )

        assert res.status_code == 404
        assert "message" in res.json()

    def test_should_get_sport_session(self, seed_sport_sessions):
        client = TestClient(app)

        res = client.get(f"/sport-session/{self.active_session_id}")

        assert res.status_code == 200
        assert "session_id" in res.json()
        assert "sport_id" in res.json()
        assert "user_id" in res.json()
        assert "started_at" in res.json()
        assert "duration" in res.json()
        assert "steps" in res.json()
        assert "distance" in res.json()
        assert "calories" in res.json()
        assert "average_speed" in res.json()
        assert "min_heartrate" in res.json()
        assert "max_heartrate" in res.json()
        assert "avg_heartrate" in res.json()

    def test_get_sport_session_should_fail_if_not_the_owner(self, seed_sport_sessions):
        client = TestClient(app)

        res = client.get(f"/sport-session/{self.active_session_id}", headers={"user-id": str(uuid.uuid4())})

        assert res.status_code == 403
        assert "error" in res.json()

    def test_get_sport_session_should_fail_if_not_found(self):
        client = TestClient(app)

        res = client.get(f"/sport-session/{uuid.uuid4()}")

        assert res.status_code == 404
        assert "message" in res.json()
