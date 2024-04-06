import os
import unittest
import uuid
import json
from asyncio import get_event_loop

import faker
import pytest
from async_asgi_testclient import TestClient
from sqlalchemy import create_engine, StaticPool
from sqlalchemy.orm import sessionmaker

from app.models.users import User
from main import app
from app.config.db import base, get_db
from tests.utils.users_util import generate_random_user_create_data, generate_random_user_additional_information


class Constants:
    USERS_BASE_PATH = "/users"
    TEXT_EVENT_STREAM = "text/event-stream"
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


def is_json(myjson):
    try:
        json.loads(myjson)
    except ValueError as e:
        return False
    return True


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
        assert response.status_code == 200
        assert Constants.TEXT_EVENT_STREAM in response.headers["content-type"]

        sse_responses = response.text.split("\r\n\r\n")
        processing_response = {"status": "processing", "message": "Processing..."}

        assert json.dumps(processing_response) in sse_responses[0]
        assert '"status": "success"' in sse_responses[1]
        assert '"message": "User created"' in sse_responses[1]
        assert '"data":' in sse_responses[1]
        assert '"id":' in sse_responses[1]
        assert f'"first_name": "{user_data.first_name}"' in sse_responses[1]
        assert f'"last_name": "{user_data.last_name}"' in sse_responses[1]
        assert f'"email": "{user_data.email}"' in sse_responses[1]


@pytest.mark.asyncio
async def test_register_user_repeated_user(test_db):
    async with TestClient(app) as client:
        user_data = generate_random_user_create_data(fake)
        processing_response = {"status": "processing", "message": "Processing..."}

        response = await client.post(f"{Constants.USERS_BASE_PATH}", json=user_data.__dict__)
        sse_responses = response.text.split("\r\n\r\n")

        assert response.status_code == 200
        assert Constants.TEXT_EVENT_STREAM in response.headers["content-type"]
        assert json.dumps(processing_response) in sse_responses[0]
        assert '"message": "User created"' in sse_responses[1]

        response = await client.post(Constants.USERS_BASE_PATH, json=user_data.__dict__)
        sse_responses = response.text.split("\r\n\r\n")
        user_exists_response = {"status": "error", "message": "User already exists"}

        assert response.status_code == 200
        assert Constants.TEXT_EVENT_STREAM in response.headers["content-type"]
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

        assert response.status_code == 200
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
