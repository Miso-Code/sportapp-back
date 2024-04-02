import os
import unittest
import uuid
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

        response = await client.post("/users/", json=user_data.__dict__)

        assert response.status_code == 200
        assert "text/event-stream" in response.headers["content-type"]
        assert "User created" in response.text


@pytest.mark.asyncio
async def test_register_user_repeated_user(test_db):
    async with TestClient(app) as client:
        user_data = generate_random_user_create_data(fake)

        response = await client.post("/users/", json=user_data.__dict__)

        assert response.status_code == 200
        assert "text/event-stream" in response.headers["content-type"]
        assert "User created" in response.text

        response = await client.post("/users/", json=user_data.__dict__)

        assert response.status_code == 200
        assert "text/event-stream" in response.headers["content-type"]
        assert "User already exists" in response.text


@pytest.mark.asyncio
async def test_register_user_with_invalid_password(test_db):
    async with TestClient(app) as client:
        user_data = generate_random_user_create_data(fake)
        user_data.password = "not_strong"

        response = await client.post("/users/", json=user_data.__dict__)
        response_json = response.json()

        assert response.status_code == 400
        assert "application/json" in response.headers["content-type"]
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

        response = await client.patch(f"/users/{user_id}/complete-registration", json=additional_info_json)
        response_json = response.json()

        assert response.status_code == 200
        assert "application/json" in response.headers["content-type"]
        assert response_json["identification_type"] == additional_info.identification_type.value
        assert response_json["identification_number"] == additional_info.identification_number
        assert response_json["gender"] == additional_info.gender.value
        assert response_json["country_of_birth"] == additional_info.country_of_birth
        assert response_json["city_of_birth"] == additional_info.city_of_birth
        assert response_json["country_of_residence"] == additional_info.country_of_residence
        assert response_json["city_of_residence"] == additional_info.city_of_residence
        assert response_json["residence_age"] == additional_info.residence_age
        assert response_json["birth_date"] == additional_info.birth_date
