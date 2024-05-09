import json
import uuid
from unittest.mock import patch, MagicMock

import faker
from sqlalchemy.orm import Session

from app.routes.sport_sessions import (
    start_sport_session,
    add_locations_to_sport_session,
    finish_sport_session,
    get_sport_session,
    get_all_sport_sessions,
    get_active_sport_sessions,
)

from app.models.schemas.schema import SportSessionStart

fake = faker.Faker()


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

    @patch("app.services.sport_sessions.SportSessionService.get_sport_sessions")
    async def test_get_sport_sessions(self, mocked_get_sport_sessions):
        mocked_db_session = MagicMock(spec=Session)
        data = [{"id": "1", "user_id": "1234", "locations": []}, {"id": "2", "user_id": "1234", "locations": []}]
        mocked_get_sport_sessions.return_value = data
        response = await get_all_sport_sessions(user_id=uuid.uuid4(), db=mocked_db_session)
        json_response = json.loads(response.body)

        assert response.status_code == 200
        assert len(json_response) == 2

    @patch("app.services.sport_sessions.SportSessionService.get_active_sport_sessions")
    @patch("app.utils.utils.validate_api_key")
    async def test_get_active_sport_sessions(self, mocked_validate_api_key, mocked_get_active_sport_sessions):
        api_key = fake.sha256()
        mocked_validate_api_key.side_effect = lambda x: x

        fake_users = [
            {"user_id": fake.uuid4(), "latitude": float(fake.latitude()), "longitude": float(fake.longitude())},
            {"user_id": fake.uuid4(), "latitude": float(fake.latitude()), "longitude": float(fake.longitude())},
            {"user_id": fake.uuid4(), "latitude": float(fake.latitude()), "longitude": float(fake.longitude())},
        ]
        mocked_get_active_sport_sessions.return_value = fake_users

        response = await get_active_sport_sessions(db=MagicMock(spec=Session), x_api_key=api_key)
        response_json = json.loads(response.body)

        assert response.status_code == 200
        assert response_json == fake_users
