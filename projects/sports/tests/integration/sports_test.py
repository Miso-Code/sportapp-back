import uuid

from pytest import fixture

from main import app
from app.models.model import Sport
from app.config.db import session_local
from fastapi.testclient import TestClient


class TestSports:
    @fixture
    def seed_sports(self):
        self.sports = [Sport(sport_id=uuid.uuid4(), name="Football"), Sport(sport_id=uuid.uuid4(), name="Basketball")]
        db = session_local()

        db.bulk_save_objects(self.sports)
        yield
        db.query(Sport).delete()
        db.close()

    def test_should_return_all(self, seed_sports):
        client = TestClient(app)

        res = client.get("/sports/")

        assert res.status_code == 200
        assert res.json() == [{"sport_id": str(sport.sport_id), "name": sport.name} for sport in self.sports]

    def test_should_return_by_id(self, seed_sports):
        client = TestClient(app)
        sport_id = str(self.sports[0].sport_id)
        res = client.get(f"/sports/{sport_id}/")

        assert res.status_code == 200
        assert res.json() == {"sport_id": sport_id, "name": self.sports[0].name}

    def test_should_return_not_found(self):
        client = TestClient(app)
        sport_id = uuid.uuid4()
        res = client.get(f"/sports/{sport_id}/")

        assert res.status_code == 404

    def test_should_return_bad_request_if_no_uuid(self):
        client = TestClient(app)
        sport_id = "notanuuid"
        res = client.get(f"/sports/{sport_id}/")

        assert res.status_code == 422
