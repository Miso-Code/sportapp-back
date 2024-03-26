import json
from unittest.mock import patch

from sqlalchemy.orm import Session

from app.routes.sports import get_all_sports, get_sport_by_id


class TestSportRoutes:
    @patch("app.services.sports.SportService.get_sports", return_value=[])
    async def test_get_all_routes(self, mocked_db_session: Session):
        response = await get_all_sports(db=mocked_db_session)
        assert json.loads(response.body) == []
        assert response.status_code == 200

    @patch("app.services.sports.SportService.get_sport_by_id", return_value={"sport_id": "1", "name": "Football"})
    async def test_get_sport_by_id(self, mocked_db_session: Session):
        sport_id = "1"
        response = await get_sport_by_id(sport_id, db=mocked_db_session)
        assert json.loads(response.body) == {"sport_id": "1", "name": "Football"}
        assert response.status_code == 200
