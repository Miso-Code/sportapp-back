import faker
import pytest
from fastapi.testclient import TestClient
from mock.mock import MagicMock
from sqlalchemy import create_engine, StaticPool
from sqlalchemy.orm import sessionmaker
from app.config.db import base, get_db


class Constants:
    ALERTS_BASE_PATH = "/alerts"
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


@pytest.fixture()
def db_fixture():
    base.metadata.create_all(bind=test_engine)
    yield
    base.metadata.drop_all(bind=test_engine)


class MockFirebaseWrapper:
    def __init__(self):
        self.messaging = MagicMock()
        self.credentials = MagicMock()
        self.initialize_app = MagicMock()


def test_register_device(db_fixture, mocker):
    mocker.patch("app.wrapper.firebase_wrapper.FirebaseWrapper", MockFirebaseWrapper)
    from main import app

    with TestClient(app) as client:
        user_id = fake.uuid4()
        device_token = fake.uuid4()

        register_data = {
            "device_token": device_token,
        }

        response = client.post(
            f"{Constants.ALERTS_BASE_PATH}/register-device",
            json=register_data,
            headers={"Content-Type": Constants.APPLICATION_JSON, "user-id": user_id},
        )

        response_json = response.json()

        assert response.status_code == 201
        assert response_json["device_token"] == device_token
        assert response_json["user_id"] == user_id
        assert response_json["enabled"] is True


def test_disable_device(db_fixture, mocker):
    mocker.patch("app.wrapper.firebase_wrapper.FirebaseWrapper", MockFirebaseWrapper)
    mocker.patch("boto3.Session", MagicMock)
    from main import app

    with TestClient(app) as client:
        user_id = fake.uuid4()
        device_token = fake.uuid4()

        register_data = {
            "device_token": device_token,
        }

        response = client.post(
            f"{Constants.ALERTS_BASE_PATH}/register-device",
            json=register_data,
            headers={"Content-Type": Constants.APPLICATION_JSON, "user-id": user_id},
        )

        response_json = response.json()

        assert response.status_code == 201
        assert response_json["device_token"] == device_token
        assert response_json["user_id"] == user_id
        assert response_json["enabled"] is True

        response = client.put(
            f"{Constants.ALERTS_BASE_PATH}/disable-device",
            headers={"Content-Type": Constants.APPLICATION_JSON, "user-id": user_id},
        )

        response_json = response.json()

        assert response.status_code == 200
        assert response_json["device_token"] == device_token
        assert response_json["user_id"] == user_id
        assert response_json["enabled"] is False


def test_get_device(db_fixture, mocker):
    mocker.patch("app.wrapper.firebase_wrapper.FirebaseWrapper", MockFirebaseWrapper)
    from main import app

    with TestClient(app) as client:
        user_id = fake.uuid4()
        device_token = fake.uuid4()

        register_data = {
            "device_token": device_token,
        }

        response = client.post(
            f"{Constants.ALERTS_BASE_PATH}/register-device",
            json=register_data,
            headers={"Content-Type": Constants.APPLICATION_JSON, "user-id": user_id},
        )

        response_json = response.json()

        assert response.status_code == 201
        assert response_json["device_token"] == device_token
        assert response_json["user_id"] == user_id
        assert response_json["enabled"] is True

        response = client.get(
            f"{Constants.ALERTS_BASE_PATH}/device",
            headers={"Content-Type": Constants.APPLICATION_JSON, "user-id": user_id},
        )

        response_json = response.json()

        assert response.status_code == 200
        assert response_json["device_token"] == device_token
        assert response_json["user_id"] == user_id
        assert response_json["enabled"] is True
