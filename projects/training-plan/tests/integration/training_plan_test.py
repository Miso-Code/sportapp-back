import datetime
import uuid

from faker import Faker
from pytest import fixture

from main import app
from app.models.training_plan import TrainingPlanSession
from app.config.db import session_local
from fastapi.testclient import TestClient

from tests.utils.training_plan_utils import generate_random_training_plan_session, generate_random_training_plan_create_data, generate_random_training_plan_create_data_dict

fake = Faker()


class TestSportSessions:
    @fixture(autouse=True)
    def seed_db(self):
        self.user_id = uuid.uuid4()

        training_plan_sessions = [generate_random_training_plan_session(fake) for _ in range(fake.random_int(min=1, max=7))]

        for training_plan_session in training_plan_sessions:
            training_plan_session.user_id = self.user_id

        session = session_local()
        session.add_all(training_plan_sessions)
        session.commit()
        [session.refresh(training_plan_session) for training_plan_session in training_plan_sessions]
        self.training_plan_sessions = training_plan_sessions

    def test_should_create_training_plan(self):
        client = TestClient(app)

        training_plan_dict = generate_random_training_plan_create_data_dict(fake)
        training_plan_dict["training_objective"] = training_plan_dict["training_objective"].value

        res = client.post("/training-plans/", json=training_plan_dict, headers={"user-id": str(self.user_id)})
        json_response = res.json()

        assert res.status_code == 200
        assert len(json_response) == len(training_plan_dict["available_weekdays"])
        for training_plan_session in json_response:
            assert training_plan_session["weekday"] in training_plan_dict["available_weekdays"]
            assert training_plan_session["start_time"] == training_plan_dict["preferred_training_start_time"]
            assert training_plan_session["warm_up"] is not None
            assert training_plan_session["cardio"] is not None
            assert training_plan_session["strength"] is not None
            assert training_plan_session["cool_down"] is not None
            assert training_plan_session["user_id"] == str(self.user_id)

    def test_should_fail_create_training_plan_with_invalid_values(self):
        client = TestClient(app)

        training_plan_dict = generate_random_training_plan_create_data_dict(fake)
        training_plan_dict["training_objective"] = "invalid_value"
        training_plan_dict["available_weekdays"] = ["INVALID"]

        res = client.post("/training-plans/", json=training_plan_dict, headers={"user-id": str(self.user_id)})
        json_response = res.json()

        assert res.status_code == 400

    def test_should_fail_with_empty_body(self):
        client = TestClient(app)

        res = client.post("/training-plans/", json={}, headers={"user-id": str(self.user_id)})
        json_response = res.json()

        assert res.status_code == 400

    def test_should_get_training_plan(self):
        client = TestClient(app)

        res = client.get("/training-plans/", headers={"user-id": str(self.user_id)})
        json_response = res.json()

        assert res.status_code == 200
        assert len(json_response) == len(self.training_plan_sessions)
        for training_plan_session in json_response:
            assert training_plan_session["weekday"] in [training_plan_session.weekday for training_plan_session in self.training_plan_sessions]
            assert training_plan_session["start_time"] in [training_plan_session.start_time for training_plan_session in self.training_plan_sessions]
            assert training_plan_session["warm_up"] in [training_plan_session.warm_up for training_plan_session in self.training_plan_sessions]
            assert training_plan_session["cardio"] in [training_plan_session.cardio for training_plan_session in self.training_plan_sessions]
            assert training_plan_session["strength"] in [training_plan_session.strength for training_plan_session in self.training_plan_sessions]
            assert training_plan_session["cool_down"] in [training_plan_session.cool_down for training_plan_session in self.training_plan_sessions]
            assert training_plan_session["user_id"] == str(self.user_id)

    def test_should_return_empty_list_when_user_has_no_training_plan(self):
        client = TestClient(app)

        res = client.get("/training-plans/", headers={"user-id": str(uuid.uuid4())})
        json_response = res.json()

        assert res.status_code == 200
        assert len(json_response) == 0

    def test_should_fail_get_training_plan_with_invalid_user_id(self):
        client = TestClient(app)

        res = client.get("/training-plans/", headers={"user-id": "invalid_user_id"})
        json_response = res.json()

        assert res.status_code == 400
