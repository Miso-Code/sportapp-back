import faker
import pytest
from fastapi.testclient import TestClient
from sqlalchemy import create_engine, StaticPool
from sqlalchemy.orm import sessionmaker

from app.models.model import SportEvent
from app.models.schemas.schema import SportEventCreate
from main import app
from app.config.db import base, get_db
from tests.utils.sport_events_util import generate_random_sport_event_data, generate_random_sport_event


class Constants:
    SPORT_EVENTS_BASE_PATH = "/sport-events"
    APPLICATION_JSON = "application/json"


fake = faker.Faker()

# use an in-memory SQLite for testing
SQLALCHEMY_DATABASE_URL = "sqlite://"

test_engine = create_engine(
    SQLALCHEMY_DATABASE_URL,
    connect_args={"check_same_thread": False},
    poolclass=StaticPool,
)


def override_get_db():
    try:
        db = TestingSessionLocal()
        yield db
    finally:
        db.close()


TestingSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=test_engine)

base.metadata.create_all(bind=test_engine)

app.dependency_overrides[get_db] = override_get_db

client = TestClient(app)
client.headers = {"X-API-Key": "secret"}


@pytest.fixture()
def test_db():
    base.metadata.create_all(bind=test_engine)
    yield
    base.metadata.drop_all(bind=test_engine)


def test_create_sport_event(test_db):
    event: SportEventCreate = generate_random_sport_event_data(fake)
    event_data = {
        "sport_id": str(event.sport_id),
        "location_latitude": event.location_latitude,
        "location_longitude": event.location_longitude,
        "start_date": event.start_date.isoformat(),
        "end_date": event.end_date.isoformat(),
        "title": event.title,
        "capacity": event.capacity,
        "description": event.description,
    }

    response = client.post(
        f"{Constants.SPORT_EVENTS_BASE_PATH}/",
        json=event_data,
    )
    response_json = response.json()

    assert response.status_code == 201
    assert "event_id" in response_json
    assert response_json["sport_id"] == event_data["sport_id"]
    assert response_json["location_latitude"] == event_data["location_latitude"]
    assert response_json["location_longitude"] == event_data["location_longitude"]
    assert response_json["start_date"] == event_data["start_date"]
    assert response_json["end_date"] == event_data["end_date"]
    assert response_json["title"] == event_data["title"]
    assert response_json["capacity"] == event_data["capacity"]
    assert response_json["description"] == event_data["description"]


def test_get_sport_events(test_db):
    helper_db = TestingSessionLocal()
    event: SportEvent = generate_random_sport_event(fake)
    event_2: SportEvent = generate_random_sport_event(fake)
    event_3: SportEvent = generate_random_sport_event(fake)

    helper_db.add(event)
    helper_db.add(event_2)
    helper_db.add(event_3)
    helper_db.commit()

    response = client.get(f"{Constants.SPORT_EVENTS_BASE_PATH}/")
    response_json = response.json()

    assert response.status_code == 200
    assert len(response_json) == 3
    for event in response_json:
        assert "event_id" in event
        assert "sport_id" in event
        assert "location_latitude" in event
        assert "location_longitude" in event
        assert "start_date" in event
        assert "end_date" in event
        assert "title" in event
        assert "capacity" in event
        assert "description" in event


def test_get_sport_event(test_db):
    helper_db = TestingSessionLocal()
    event: SportEvent = generate_random_sport_event(fake)

    helper_db.add(event)
    helper_db.commit()

    response = client.get(f"{Constants.SPORT_EVENTS_BASE_PATH}/{event.event_id}")
    response_json = response.json()

    assert response.status_code == 200
    assert response_json["event_id"] == str(event.event_id)
    assert response_json["sport_id"] == str(event.sport_id)
    assert response_json["location_latitude"] == event.location_latitude
    assert response_json["location_longitude"] == event.location_longitude
    assert response_json["start_date"] == event.start_date.isoformat()
    assert response_json["end_date"] == event.end_date.isoformat()
    assert response_json["title"] == event.title
    assert response_json["capacity"] == event.capacity
    assert response_json["description"] == event.description
