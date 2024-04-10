import json
import uuid
from unittest.mock import patch, MagicMock

from sqlalchemy.orm import Session

from app.routes.sport_sessions import start_sport_session, add_locations_to_sport_session, finish_sport_session, get_sport_session

from app.models.schemas.schema import SportSessionStart


class TestSportRoutes:
    @patch("app.services.sport_sessions.SportSessionService.start_sport_session", return_value={})
    async def test_start_sport_session(self, mocked_db_session: Session):
        response = await start_sport_session(sport_session={}, db=mocked_db_session)
        assert json.loads(response.body) == {}
        assert response.status_code == 200

    @patch("app.services.sport_sessions.SportSessionService.start_sport_session", return_value={})
    async def test_start_sport_session_should_fail_when_no_owner(self, mocked_db_session: Session):
        sport_session = MagicMock(spec=SportSessionStart)
        sport_session.user_id = uuid.uuid4()

        response = await start_sport_session(sport_session=sport_session, user_id=uuid.uuid4(), db=mocked_db_session)
        assert "error" in json.loads(response.body)
        assert response.status_code == 403

    @patch("app.services.sport_sessions.SportSessionService.add_location_to_sport_session", return_value={})
    async def test_add_locations_to_sport_session(self, mocked_db_session: Session):
        response = await add_locations_to_sport_session(sport_session_id=uuid.uuid4(), location={}, db=mocked_db_session)
        assert json.loads(response.body) == {}
        assert response.status_code == 200

    @patch("app.services.sport_sessions.SportSessionService.add_location_to_sport_session", return_value={})
    @patch("app.services.sport_sessions.SportSessionService.get_sport_session")
    async def test_add_locations_to_sport_session_should_fail_when_no_owner(self, mocked_db_session: Session, mocked_get_sport_session: MagicMock):
        mocked_get_sport_session.return_value = {"user_id": uuid.uuid4()}
        response = await add_locations_to_sport_session(sport_session_id=uuid.uuid4(), location={}, user_id=uuid.uuid4(), db=mocked_db_session)
        assert "error" in json.loads(response.body)
        assert response.status_code == 403

    @patch("app.services.sport_sessions.SportSessionService.finish_sport_session", return_value={})
    async def test_finish_sport_session(self, mocked_db_session: Session):
        response = await finish_sport_session(sport_session_id=uuid.uuid4(), sport_session_input={}, db=mocked_db_session)
        assert json.loads(response.body) == {}
        assert response.status_code == 200

    @patch("app.services.sport_sessions.SportSessionService.finish_sport_session", return_value={})
    @patch("app.services.sport_sessions.SportSessionService.get_sport_session")
    async def test_finish_sport_session_should_fail_when_no_owner(self, mocked_db_session: Session, mocked_get_sport_session: MagicMock):
        mocked_get_sport_session.return_value = {"user_id": uuid.uuid4()}
        response = await finish_sport_session(sport_session_id=uuid.uuid4(), sport_session_input={}, user_id=uuid.uuid4(), db=mocked_db_session)
        assert "error" in json.loads(response.body)
        assert response.status_code == 403

    @patch("app.services.sport_sessions.SportSessionService.get_sport_session", return_value={})
    async def test_get_sport_session(self, mocked_db_session: Session):
        response = await get_sport_session(sport_session_id=uuid.uuid4(), db=mocked_db_session)
        assert json.loads(response.body) == {}
        assert response.status_code == 200

    @patch("app.services.sport_sessions.SportSessionService.get_sport_session", return_value={"user_id": "1234"})
    async def test_get_sport_session_should_fail_when_no_owner(self, mocked_db_session: Session):
        response = await get_sport_session(sport_session_id=uuid.uuid4(), user_id=uuid.uuid4(), db=mocked_db_session)
        assert "error" in json.loads(response.body)
        assert response.status_code == 403
