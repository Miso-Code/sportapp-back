from mock_alchemy.mocking import UnifiedAlchemyMagicMock
from pytest import fixture
from os import environ

from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker


# For unit test let's use a mocked db
@fixture(autouse=True)
def mocked_db_session() -> UnifiedAlchemyMagicMock:
    session = UnifiedAlchemyMagicMock()
    return session


# For integration test let's use an in memory sqlite
environ["DB_DRIVER"] = "test"
