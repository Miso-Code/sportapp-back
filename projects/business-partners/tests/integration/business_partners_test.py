import faker
import pytest
from fastapi.testclient import TestClient
from sqlalchemy import create_engine, StaticPool
from sqlalchemy.orm import sessionmaker

from http import HTTPStatus

from app.config.settings import Config
from main import app
from app.config.db import base, get_db
from tests.utils.business_partners_util import generate_random_business_partner_create_data


class Constants:
    BUSINESS_PARTNERS_BASE_PATH = "/business-partners"
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


@pytest.fixture()
def test_db():
    base.metadata.create_all(bind=test_engine)
    yield
    base.metadata.drop_all(bind=test_engine)


def test_create_business_partner(test_db):
    business_partner_create = generate_random_business_partner_create_data(fake)
    business_partner_create_dict = {
        "business_partner_name": business_partner_create.business_partner_name,
        "email": business_partner_create.email,
        "password": business_partner_create.password,
    }

    response = client.post(f"{Constants.BUSINESS_PARTNERS_BASE_PATH}/registration", json=business_partner_create_dict)
    response_json = response.json()

    print(response.json())

    assert response.status_code == HTTPStatus.CREATED
    assert response_json["business_partner_name"] == business_partner_create.business_partner_name
    assert response_json["email"] == business_partner_create.email
    assert response_json["business_partner_id"] is not None
    assert "hashed_password" not in response_json


def test_create_business_partner_with_existing_email(test_db):
    business_partner_create = generate_random_business_partner_create_data(fake)
    business_partner_create_dict = {
        "business_partner_name": business_partner_create.business_partner_name,
        "email": business_partner_create.email,
        "password": business_partner_create.password,
    }

    response = client.post(f"{Constants.BUSINESS_PARTNERS_BASE_PATH}/registration", json=business_partner_create_dict)

    assert response.status_code == HTTPStatus.CREATED

    business_partner_repeated_create_dict = {"business_partner_name": fake.company(), "email": business_partner_create.email, "password": fake.password()}

    response = client.post(f"{Constants.BUSINESS_PARTNERS_BASE_PATH}/registration", json=business_partner_repeated_create_dict)

    response_json = response.json()

    assert response.status_code == HTTPStatus.BAD_REQUEST
    assert response_json["message"] == "Business partner with this email already exists"


def test_login_business_partner(test_db):
    business_partner_create = generate_random_business_partner_create_data(fake)
    business_partner_create_dict = {
        "business_partner_name": business_partner_create.business_partner_name,
        "email": business_partner_create.email,
        "password": business_partner_create.password,
    }

    response = client.post(f"{Constants.BUSINESS_PARTNERS_BASE_PATH}/registration", json=business_partner_create_dict)

    assert response.status_code == HTTPStatus.CREATED

    login_business_partner_dict = {"email": business_partner_create.email, "password": business_partner_create.password}

    response = client.post(f"{Constants.BUSINESS_PARTNERS_BASE_PATH}/login", json=login_business_partner_dict)

    response_json = response.json()

    assert response.status_code == HTTPStatus.OK
    assert Constants.APPLICATION_JSON in response.headers["content-type"]
    assert response_json["access_token"] is not None
    assert response_json["access_token_expires_minutes"] is not None
    assert response_json["access_token_expires_minutes"] == Config.ACCESS_TOKEN_EXPIRE_MINUTES
    assert response_json["refresh_token"] is not None
    assert response_json["refresh_token_expires_minutes"] is not None
    assert response_json["refresh_token_expires_minutes"] == Config.REFRESH_TOKEN_EXPIRE_MINUTES


def test_login_business_partner_with_incorrect_password(test_db):
    login_business_partner_dict = {"email": fake.email(), "password": fake.password()}

    response = client.post(f"{Constants.BUSINESS_PARTNERS_BASE_PATH}/login", json=login_business_partner_dict)

    response_json = response.json()

    assert response.status_code == HTTPStatus.UNAUTHORIZED
    assert response_json["message"] == "Invalid email or password"
