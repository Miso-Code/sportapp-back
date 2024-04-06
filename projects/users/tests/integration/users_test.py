import json
from asyncio import get_event_loop

import faker
import pytest
from async_asgi_testclient import TestClient
from sqlalchemy import create_engine, StaticPool
from sqlalchemy.orm import sessionmaker

from http import HTTPStatus

from app.config.settings import Config
from app.models.users import User
from app.security.passwords import PasswordManager
from main import app
from app.config.db import base, get_db
from tests.utils.users_util import generate_random_user_create_data, generate_random_user_additional_information


class Constants:
    USERS_BASE_PATH = "/users"
    TEXT_EVENT_STREAM = "text/event-stream"
    APPLICATION_JSON = "application/json"
    USER_CREATED_MESSAGE = "User created"
    USER_CREATED_STATUS = "success"
    USER_ALREADY_EXISTS_MESSAGE = "User already exists"
    ERROR_STATUS = "error"
    PROCESSING_MESSAGE = "Processing..."


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


@pytest.fixture(scope="module")
def event_loop():
    loop = get_event_loop()
    yield loop


@pytest.fixture()
def test_db():
    base.metadata.create_all(bind=test_engine)
    yield
    base.metadata.drop_all(bind=test_engine)


@pytest.mark.asyncio
async def test_register_user(test_db):
    async with TestClient(app) as client:
        user_data = generate_random_user_create_data(fake)

        response = await client.post(Constants.USERS_BASE_PATH, json=user_data.__dict__)
        assert response.status_code == HTTPStatus.OK
        assert Constants.TEXT_EVENT_STREAM in response.headers["content-type"]

        sse_responses = response.text.split("\r\n\r\n")
        processing_response = {"status": "processing", "message": Constants.PROCESSING_MESSAGE}
        created_response = json.loads(sse_responses[1][6:])

        assert json.dumps(processing_response) in sse_responses[0]
        assert created_response["status"] == Constants.USER_CREATED_STATUS
        assert created_response["message"] == Constants.USER_CREATED_MESSAGE
        assert created_response["data"]["id"] is not None
        assert created_response["data"]["first_name"] == user_data.first_name
        assert created_response["data"]["last_name"] == user_data.last_name
        assert created_response["data"]["email"] == user_data.email


@pytest.mark.asyncio
async def test_register_user_repeated_user(test_db):
    async with TestClient(app) as client:
        user_data = generate_random_user_create_data(fake)
        processing_response = {"status": "processing", "message": Constants.PROCESSING_MESSAGE}

        first_create_user_response = await client.post(f"{Constants.USERS_BASE_PATH}", json=user_data.__dict__)
        sse_responses = first_create_user_response.text.split("\r\n\r\n")
        created_response = json.loads(sse_responses[1][6:])

        assert first_create_user_response.status_code == HTTPStatus.OK
        assert Constants.TEXT_EVENT_STREAM in first_create_user_response.headers["content-type"]
        assert json.dumps(processing_response) in sse_responses[0]
        assert created_response["status"] == Constants.USER_CREATED_STATUS
        assert created_response["message"] == Constants.USER_CREATED_MESSAGE

        second_create_user_response = await client.post(Constants.USERS_BASE_PATH, json=user_data.__dict__)
        sse_responses = second_create_user_response.text.split("\r\n\r\n")
        user_exists_response = {"status": "error", "message": "User already exists"}

        assert second_create_user_response.status_code == HTTPStatus.OK
        assert Constants.TEXT_EVENT_STREAM in second_create_user_response.headers["content-type"]
        assert json.dumps(processing_response) in sse_responses[0]
        assert json.dumps(user_exists_response) in sse_responses[1]


@pytest.mark.asyncio
async def test_register_user_with_invalid_password(test_db):
    async with TestClient(app) as client:
        user_data = generate_random_user_create_data(fake)
        user_data.password = "not_strong"

        response = await client.post(Constants.USERS_BASE_PATH, json=user_data.__dict__)
        response_json = response.json()

        assert response.status_code == 400
        assert Constants.APPLICATION_JSON in response.headers["content-type"]
        assert (
            "Password must be between 8 and 64 characters long and contain at least one digit, one lowercase "
            "letter, one uppercase letter, and one special character" in response_json["message"]
        )


@pytest.mark.asyncio
async def test_complete_user_registration(test_db):
    async with TestClient(app) as client:
        helper_db = TestingSessionLocal()
        user_data = generate_random_user_create_data(fake)
        created_user = User(email=user_data.email, first_name=user_data.first_name, last_name=user_data.last_name, hashed_password=user_data.password)
        helper_db.add(created_user)
        helper_db.commit()

        user_id = created_user.user_id

        additional_info = generate_random_user_additional_information(fake)
        additional_info_json = {
            "identification_type": additional_info.identification_type.value,
            "identification_number": additional_info.identification_number,
            "gender": additional_info.gender.value,
            "country_of_birth": additional_info.country_of_birth,
            "city_of_birth": additional_info.city_of_birth,
            "country_of_residence": additional_info.country_of_residence,
            "city_of_residence": additional_info.city_of_residence,
            "residence_age": additional_info.residence_age,
            "birth_date": additional_info.birth_date,
        }

        response = await client.patch(f"{Constants.USERS_BASE_PATH}/{user_id}/complete-registration", json=additional_info_json)
        response_json = response.json()

        assert response.status_code == HTTPStatus.OK
        assert Constants.APPLICATION_JSON in response.headers["content-type"]
        assert response_json["identification_type"] == additional_info.identification_type.value
        assert response_json["identification_number"] == additional_info.identification_number
        assert response_json["gender"] == additional_info.gender.value
        assert response_json["country_of_birth"] == additional_info.country_of_birth
        assert response_json["city_of_birth"] == additional_info.city_of_birth
        assert response_json["country_of_residence"] == additional_info.country_of_residence
        assert response_json["city_of_residence"] == additional_info.city_of_residence
        assert response_json["residence_age"] == additional_info.residence_age
        assert response_json["birth_date"] == additional_info.birth_date


@pytest.mark.asyncio
async def test_authenticate_user_email_password(test_db):
    async with TestClient(app) as client:
        helper_db = TestingSessionLocal()
        user_data = generate_random_user_create_data(fake)
        created_user = User(
            email=user_data.email,
            first_name=user_data.first_name,
            last_name=user_data.last_name,
            hashed_password=PasswordManager.get_password_hash(user_data.password),
        )
        helper_db.add(created_user)
        helper_db.commit()

        response = await client.post(f"{Constants.USERS_BASE_PATH}/login", json={"email": user_data.email, "password": user_data.password})
        response_json = response.json()

        assert response.status_code == HTTPStatus.OK
        assert Constants.APPLICATION_JSON in response.headers["content-type"]
        assert response_json["access_token"] is not None
        assert response_json["access_token_expires_minutes"] is not None
        assert response_json["access_token_expires_minutes"] == Config.ACCESS_TOKEN_EXPIRE_MINUTES
        assert response_json["refresh_token"] is not None
        assert response_json["refresh_token_expires_minutes"] is not None
        assert response_json["refresh_token_expires_minutes"] == Config.REFRESH_TOKEN_EXPIRE_MINUTES


@pytest.mark.asyncio
async def test_authenticate_user_email_password_wrong_password(test_db):
    async with TestClient(app) as client:
        helper_db = TestingSessionLocal()
        user_data = generate_random_user_create_data(fake)
        created_user = User(
            email=user_data.email,
            first_name=user_data.first_name,
            last_name=user_data.last_name,
            hashed_password=PasswordManager.get_password_hash(user_data.password),
        )
        helper_db.add(created_user)
        helper_db.commit()

        response = await client.post(f"{Constants.USERS_BASE_PATH}/login", json={"email": user_data.email, "password": "wrong_password"})
        response_json = response.json()

        assert response.status_code == HTTPStatus.UNAUTHORIZED
        assert Constants.APPLICATION_JSON in response.headers["content-type"]
        assert response_json["message"] == "Invalid email or password"


@pytest.mark.asyncio
async def test_authenticate_user_email_password_wrong_user(test_db):
    async with TestClient(app) as client:
        response = await client.post(f"{Constants.USERS_BASE_PATH}/login", json={"email": "some-email@email.com", "password": "wrong_password"})
        response_json = response.json()

        assert response.status_code == HTTPStatus.UNAUTHORIZED
        assert Constants.APPLICATION_JSON in response.headers["content-type"]
        assert response_json["message"] == "Invalid email or password"


@pytest.mark.asyncio
async def test_authenticate_user_refresh_token(test_db):
    async with TestClient(app) as client:
        helper_db = TestingSessionLocal()
        user_data = generate_random_user_create_data(fake)
        created_user = User(
            email=user_data.email,
            first_name=user_data.first_name,
            last_name=user_data.last_name,
            hashed_password=PasswordManager.get_password_hash(user_data.password),
        )
        helper_db.add(created_user)
        helper_db.commit()

        first_login_response = await client.post(f"{Constants.USERS_BASE_PATH}/login", json={"email": user_data.email, "password": user_data.password})
        first_login_response_json = first_login_response.json()

        access_token = first_login_response_json["refresh_token"]

        second_login_response = await client.post(f"{Constants.USERS_BASE_PATH}/login", json={"refresh_token": access_token})

        second_login_response_json = second_login_response.json()

        assert second_login_response.status_code == HTTPStatus.OK
        assert Constants.APPLICATION_JSON in second_login_response.headers["content-type"]
        assert second_login_response_json["access_token"] is not None
        assert second_login_response_json["access_token_expires_minutes"] is not None
        assert second_login_response_json["access_token_expires_minutes"] == Config.ACCESS_TOKEN_EXPIRE_MINUTES
        assert second_login_response_json["refresh_token"] is not None
        assert second_login_response_json["refresh_token_expires_minutes"] is not None
        assert second_login_response_json["refresh_token_expires_minutes"] == Config.REFRESH_TOKEN_EXPIRE_MINUTES


@pytest.mark.asyncio
async def test_authenticate_user_refresh_token_invalid(test_db):
    async with TestClient(app) as client:
        response = await client.post(f"{Constants.USERS_BASE_PATH}/login", json={"refresh_token": "invalid_token"})
        response_json = response.json()

        assert response.status_code == HTTPStatus.UNAUTHORIZED
        assert Constants.APPLICATION_JSON in response.headers["content-type"]
        assert response_json["message"] == "Invalid or expired refresh token"


@pytest.mark.asyncio
async def test_authenticate_user_refresh_token_expired(test_db):
    async with TestClient(app) as client:
        helper_db = TestingSessionLocal()
        user_data = generate_random_user_create_data(fake)
        created_user = User(
            email=user_data.email,
            first_name=user_data.first_name,
            last_name=user_data.last_name,
            hashed_password=PasswordManager.get_password_hash(user_data.password),
        )
        helper_db.add(created_user)
        helper_db.commit()

        Config.REFRESH_TOKEN_EXPIRE_MINUTES = 0
        first_login_response = await client.post(f"{Constants.USERS_BASE_PATH}/login", json={"email": user_data.email, "password": user_data.password})
        first_login_response_json = first_login_response.json()

        access_token = first_login_response_json["refresh_token"]

        second_login_response = await client.post(f"{Constants.USERS_BASE_PATH}/login", json={"refresh_token": access_token})
        second_login_response_json = second_login_response.json()

        assert second_login_response.status_code == HTTPStatus.UNAUTHORIZED
        assert Constants.APPLICATION_JSON in second_login_response.headers["content-type"]
        assert second_login_response_json["message"] == "Invalid or expired refresh token"
