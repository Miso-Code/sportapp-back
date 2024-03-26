import uuid

import pytest
from sqlalchemy.orm import Session

from app.exceptions.exceptions import NotFoundError
from app.models.model import Sport
from app.services.sports import SportService


class TestSportService:
    def test_get_sports_should_be_empty_if_no_sports(self, mocked_db_session: Session) -> None:
        # Given
        sport_service = SportService(mocked_db_session)
        # When
        sports = sport_service.get_sports()
        # Then
        assert sports == []

    def test_get_sports_should_return_all_sports(self, mocked_db_session: Session) -> None:
        # Given
        sport_service = SportService(mocked_db_session)
        mocked_db_session.add_all([Sport(name="Football"), Sport(name="Basketball")])
        # When
        sports = sport_service.get_sports()
        # Then
        assert [sport["name"] for sport in sports] == ["Football", "Basketball"]

    def test_get_sport_by_id_should_raise_if_not_found(self, mocked_db_session) -> None:
        # Given
        sport_service = SportService(mocked_db_session)

        with pytest.raises(NotFoundError):  # Then
            # When
            sport_service.get_sport_by_id(uuid.uuid4())

    def test_get_sport_by_id_should_return_if_found(self, mocked_db_session) -> None:
        # Given
        sport_service = SportService(mocked_db_session)
        sport_id = uuid.uuid4()
        mocked_db_session.add(Sport(sport_id=sport_id, name="Sport"))

        # When
        sport = sport_service.get_sport_by_id(sport_id)

        # Then
        assert sport["name"] == "Sport"
