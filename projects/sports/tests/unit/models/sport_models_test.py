import uuid

from app.models.model import Sport


class TestSportModel:
    def test_create_sport(self):
        sport_dict = {"sport_id": uuid.uuid4(), "name": "Football"}
        sport = Sport(sport_id=sport_dict["sport_id"], name=sport_dict["name"])
        assert sport.name == sport_dict["name"]
        assert sport.sport_id == sport_dict["sport_id"]
