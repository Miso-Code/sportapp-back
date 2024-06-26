import json
from asyncio import get_event_loop
from datetime import timedelta
from uuid import UUID

import faker
import pytest
from async_asgi_testclient import TestClient
from sqlalchemy import create_engine, StaticPool
from sqlalchemy.orm import sessionmaker

from http import HTTPStatus

from app.config.settings import Config
from app.exceptions.exceptions import NotFoundError
from app.models.mappers.user_mapper import DataClassMapper
from app.models.users import User
from app.security.passwords import PasswordManager
from app.utils import utils
from main import app
from app.config.db import base, get_db
from tests.utils.users_util import (
    generate_random_user_create_data,
    generate_random_user_additional_information,
    generate_random_user,
    generate_random_user_nutritional_limitation,
    generate_random_trainer,
    generate_random_appointment_data,
    generate_random_appointment,
)


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

        response = await client.post(f"{Constants.USERS_BASE_PATH}/registration", json=user_data.__dict__)
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

        first_create_user_response = await client.post(f"{Constants.USERS_BASE_PATH}/registration", json=user_data.__dict__)
        sse_responses = first_create_user_response.text.split("\r\n\r\n")
        created_response = json.loads(sse_responses[1][6:])

        assert first_create_user_response.status_code == HTTPStatus.OK
        assert Constants.TEXT_EVENT_STREAM in first_create_user_response.headers["content-type"]
        assert json.dumps(processing_response) in sse_responses[0]
        assert created_response["status"] == Constants.USER_CREATED_STATUS
        assert created_response["message"] == Constants.USER_CREATED_MESSAGE

        second_create_user_response = await client.post(f"{Constants.USERS_BASE_PATH}/registration", json=user_data.__dict__)
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

        response = await client.post(f"{Constants.USERS_BASE_PATH}/registration", json=user_data.__dict__)
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
            "birth_date": additional_info.birth_date.isoformat(),
        }

        client.headers["user-id"] = str(user_id)
        response = await client.patch(f"{Constants.USERS_BASE_PATH}/complete-registration", json=additional_info_json)
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
        assert response_json["birth_date"] == additional_info.birth_date.isoformat()


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


@pytest.mark.asyncio
async def test_get_user_personal_profile(test_db):
    async with TestClient(app) as client:
        helper_db = TestingSessionLocal()
        user_created = generate_random_user(fake)
        helper_db.add(user_created)
        helper_db.commit()

        client.headers["user-id"] = str(user_created.user_id)
        response = await client.get(f"{Constants.USERS_BASE_PATH}/profiles/personal")
        response_json = response.json()

        assert response.status_code == HTTPStatus.OK
        assert Constants.APPLICATION_JSON in response.headers["content-type"]
        assert response_json["email"] == user_created.email
        assert response_json["first_name"] == user_created.first_name
        assert response_json["last_name"] == user_created.last_name
        assert response_json["identification_type"] == user_created.identification_type.value
        assert response_json["identification_number"] == user_created.identification_number
        assert response_json["gender"] == user_created.gender.value
        assert response_json["country_of_birth"] == user_created.country_of_birth
        assert response_json["city_of_birth"] == user_created.city_of_birth
        assert response_json["country_of_residence"] == user_created.country_of_residence
        assert response_json["city_of_residence"] == user_created.city_of_residence
        assert response_json["residence_age"] == user_created.residence_age
        assert response_json["birth_date"] == user_created.birth_date.isoformat()

        assert getattr(response_json, "hashed_password", None) is None
        assert getattr(response_json, "weight", None) is None
        assert getattr(response_json, "height", None) is None


@pytest.mark.asyncio
async def test_get_user_personal_profile_not_found(test_db):
    async with TestClient(app) as client:
        fake_id = fake.uuid4()

        client.headers["user-id"] = str(fake_id)
        response = await client.get(f"{Constants.USERS_BASE_PATH}/profiles/personal")
        response_json = response.json()

        assert response.status_code == HTTPStatus.NOT_FOUND
        assert Constants.APPLICATION_JSON in response.headers["content-type"]
        assert response_json["message"] == f"User with id {fake_id} not found"


@pytest.mark.asyncio
async def test_get_user_sports_profile(test_db):
    async with TestClient(app) as client:
        helper_db = TestingSessionLocal()
        user_created = generate_random_user(fake)
        helper_db.add(user_created)
        helper_db.commit()

        client.headers["user-id"] = str(user_created.user_id)
        response = await client.get(f"{Constants.USERS_BASE_PATH}/profiles/sports")
        response_json = response.json()

        assert response.status_code == HTTPStatus.OK
        assert Constants.APPLICATION_JSON in response.headers["content-type"]
        assert response_json["favourite_sport_id"] == user_created.favourite_sport_id
        assert response_json["training_objective"] == user_created.training_objective.value
        assert response_json["weight"] == user_created.weight
        assert response_json["height"] == user_created.height
        assert response_json["available_training_hours"] == user_created.available_training_hours
        assert response_json["preferred_training_start_time"] == user_created.preferred_training_start_time
        assert response_json["training_limitations"] == [limitation.name for limitation in user_created.training_limitations]
        assert response_json["bmi"] == utils.calculate_bmi(user_created.weight, user_created.height)

        assert getattr(response_json, "email", None) is None
        assert getattr(response_json, "first_name", None) is None
        assert getattr(response_json, "last_name", None) is None
        assert getattr(response_json, "identification_type", None) is None
        assert getattr(response_json, "identification_number", None) is None
        assert getattr(response_json, "gender", None) is None

        response_available_weekdays = response_json["available_weekdays"]
        for weekday in response_available_weekdays:
            assert weekday in user_created.available_weekdays.split(",")


@pytest.mark.asyncio
async def test_get_user_sports_profile_not_found(test_db):
    async with TestClient(app) as client:
        fake_id = fake.uuid4()

        client.headers["user-id"] = str(fake_id)
        response = await client.get(f"{Constants.USERS_BASE_PATH}/profiles/sports")
        response_json = response.json()

        assert response.status_code == HTTPStatus.NOT_FOUND
        assert Constants.APPLICATION_JSON in response.headers["content-type"]
        assert response_json["message"] == f"User with id {fake_id} not found"


@pytest.mark.asyncio
async def test_get_user_nutritional_profile(test_db):
    async with TestClient(app) as client:
        helper_db = TestingSessionLocal()
        user_created = generate_random_user(fake)
        helper_db.add(user_created)
        helper_db.commit()

        client.headers["user-id"] = str(user_created.user_id)
        response = await client.get(f"{Constants.USERS_BASE_PATH}/profiles/nutritional")
        response_json = response.json()

        assert response.status_code == HTTPStatus.OK
        assert Constants.APPLICATION_JSON in response.headers["content-type"]
        assert response_json["food_preference"] == user_created.food_preference.value
        assert response_json["nutritional_limitations"] == [str(limitation.limitation_id) for limitation in user_created.nutritional_limitations]


@pytest.mark.asyncio
async def test_get_user_nutritional_profile_not_found(test_db):
    async with TestClient(app) as client:
        fake_id = fake.uuid4()

        client.headers["user-id"] = str(fake_id)
        response = await client.get(f"{Constants.USERS_BASE_PATH}/profiles/nutritional")
        response_json = response.json()

        assert response.status_code == HTTPStatus.NOT_FOUND
        assert Constants.APPLICATION_JSON in response.headers["content-type"]
        assert response_json["message"] == f"User with id {fake_id} not found"


@pytest.mark.asyncio
async def test_get_users_nutritional_limitations(test_db):
    async with TestClient(app) as client:
        helper_db = TestingSessionLocal()
        nutritional_limitation = generate_random_user_nutritional_limitation(fake)
        nutritional_limitation_2 = generate_random_user_nutritional_limitation(fake)
        helper_db.add(nutritional_limitation)
        helper_db.add(nutritional_limitation_2)
        helper_db.commit()

        response = await client.get(f"{Constants.USERS_BASE_PATH}/nutritional-limitations")
        response_json = response.json()

        assert response.status_code == HTTPStatus.OK
        assert Constants.APPLICATION_JSON in response.headers["content-type"]
        assert len(response_json) == 2
        assert response_json[0]["limitation_id"] == str(nutritional_limitation.limitation_id)
        assert response_json[0]["name"] == nutritional_limitation.name
        assert response_json[0]["description"] == nutritional_limitation.description
        assert response_json[1]["limitation_id"] == str(nutritional_limitation_2.limitation_id)
        assert response_json[1]["name"] == nutritional_limitation_2.name
        assert response_json[1]["description"] == nutritional_limitation_2.description


@pytest.mark.asyncio
async def test_update_user_personal_profile(test_db, mocker):
    async with TestClient(app) as client:
        helper_db = TestingSessionLocal()
        user_created = generate_random_user(fake)
        helper_db.add(user_created)
        helper_db.commit()

        new_user_data = generate_random_user(fake)
        new_user_data_json = {
            "first_name": new_user_data.first_name,
            "last_name": new_user_data.last_name,
            "identification_type": new_user_data.identification_type.value,
            "identification_number": new_user_data.identification_number,
            "gender": new_user_data.gender.value,
            "country_of_birth": new_user_data.country_of_birth,
            "city_of_birth": new_user_data.city_of_birth,
            "country_of_residence": new_user_data.country_of_residence,
            "city_of_residence": new_user_data.city_of_residence,
            "residence_age": new_user_data.residence_age,
            "birth_date": new_user_data.birth_date.isoformat(),
        }

        external_service_create_nutritional_plan = mocker.patch("app.services.external.ExternalServices.create_nutritional_plan")

        external_service_create_nutritional_plan.return_value = None

        client.headers["user-id"] = str(user_created.user_id)
        response = await client.patch(f"{Constants.USERS_BASE_PATH}/profiles/personal", json=new_user_data_json)

        response_json = response.json()

        assert response.status_code == HTTPStatus.OK
        assert Constants.APPLICATION_JSON in response.headers["content-type"]
        assert response_json["email"] == user_created.email
        assert response_json["first_name"] == new_user_data.first_name
        assert response_json["last_name"] == new_user_data.last_name
        assert response_json["identification_type"] == new_user_data.identification_type.value
        assert response_json["identification_number"] == new_user_data.identification_number
        assert response_json["gender"] == new_user_data.gender.value
        assert response_json["country_of_birth"] == new_user_data.country_of_birth
        assert response_json["city_of_birth"] == new_user_data.city_of_birth
        assert response_json["country_of_residence"] == new_user_data.country_of_residence
        assert response_json["city_of_residence"] == new_user_data.city_of_residence
        assert response_json["residence_age"] == new_user_data.residence_age
        assert response_json["birth_date"] == new_user_data.birth_date.isoformat()


@pytest.mark.asyncio
async def test_update_user_sports_profile(test_db, mocker):
    async with TestClient(app) as client:
        helper_db = TestingSessionLocal()
        user_created = generate_random_user(fake)
        helper_db.add(user_created)
        helper_db.commit()

        new_user_data = generate_random_user(fake)
        new_user_data_json = {
            "favourite_sport_id": new_user_data.favourite_sport_id,
            "training_objective": new_user_data.training_objective.value,
            "weight": new_user_data.weight,
            "height": new_user_data.height,
            "available_training_hours": new_user_data.available_training_hours,
            "training_limitations": [{"name": fake.word(), "description": fake.sentence()} for _ in range(fake.random_int(1, 4))],
            "available_weekdays": new_user_data.available_weekdays.split(","),
            "preferred_training_start_time": new_user_data.preferred_training_start_time,
        }

        external_service_get_sport = mocker.patch("app.services.external.ExternalServices.get_sport")
        external_service_get_sport.return_value = {"sport_id": new_user_data.favourite_sport_id, "name": "Some sport"}

        external_service_create_training_plan = mocker.patch("app.services.external.ExternalServices.create_training_plan")
        external_service_create_training_plan.return_value = None

        external_service_create_nutritional_plan = mocker.patch("app.services.external.ExternalServices.create_nutritional_plan")

        external_service_create_nutritional_plan.return_value = None

        client.headers["user-id"] = str(user_created.user_id)
        response = await client.patch(f"{Constants.USERS_BASE_PATH}/profiles/sports", json=new_user_data_json)

        response_json = response.json()

        assert response.status_code == HTTPStatus.OK
        assert Constants.APPLICATION_JSON in response.headers["content-type"]
        assert response_json["favourite_sport_id"] == new_user_data.favourite_sport_id
        assert response_json["training_objective"] == new_user_data.training_objective.value
        assert response_json["weight"] == new_user_data.weight
        assert response_json["height"] == new_user_data.height
        assert response_json["available_training_hours"] == new_user_data.available_training_hours
        assert response_json["bmi"] == utils.calculate_bmi(new_user_data.weight, new_user_data.height)
        assert len(response_json["training_limitations"]) == len(new_user_data_json["training_limitations"])
        assert response_json["preferred_training_start_time"] == new_user_data.preferred_training_start_time

        response_available_weekdays = response_json["available_weekdays"]
        for weekday in response_available_weekdays:
            assert weekday in new_user_data.available_weekdays.split(",")


@pytest.mark.asyncio
async def test_update_user_sports_profile_not_found_sport_id(test_db, mocker):
    async with TestClient(app) as client:
        helper_db = TestingSessionLocal()
        user_created = generate_random_user(fake)
        helper_db.add(user_created)
        helper_db.commit()

        new_user_data = generate_random_user(fake)
        new_user_data_json = {
            "favourite_sport_id": new_user_data.favourite_sport_id,
            "training_objective": new_user_data.training_objective.value,
            "weight": new_user_data.weight,
            "height": new_user_data.height,
            "available_training_hours": new_user_data.available_training_hours,
        }

        external_service_get_sport = mocker.patch("app.services.external.ExternalServices.get_sport")
        external_service_get_sport.side_effect = NotFoundError(f"Sport with id {new_user_data.favourite_sport_id} not found")

        client.headers["user-id"] = str(user_created.user_id)
        response = await client.patch(f"{Constants.USERS_BASE_PATH}/profiles/sports", json=new_user_data_json)

        response_json = response.json()

        assert response.status_code == HTTPStatus.NOT_FOUND
        assert Constants.APPLICATION_JSON in response.headers["content-type"]
        assert response_json["message"] == f"Sport with id {new_user_data.favourite_sport_id} not found"


@pytest.mark.asyncio
async def test_update_user_nutritional_profile(test_db, mocker):
    async with TestClient(app) as client:
        helper_db = TestingSessionLocal()
        user_created = generate_random_user(fake)
        helper_db.add(user_created)
        helper_db.commit()

        new_user_data = generate_random_user(fake)
        new_user_data_json = {
            "food_preference": new_user_data.food_preference.value,
            "nutritional_limitations": [str(limitation.limitation_id) for limitation in new_user_data.nutritional_limitations],
        }

        external_service_create_nutritional_plan = mocker.patch("app.services.external.ExternalServices.create_nutritional_plan")

        external_service_create_nutritional_plan.return_value = None

        client.headers["user-id"] = str(user_created.user_id)
        response = await client.patch(f"{Constants.USERS_BASE_PATH}/profiles/nutritional", json=new_user_data_json)

        response_json = response.json()

        assert response.status_code == HTTPStatus.OK
        assert Constants.APPLICATION_JSON in response.headers["content-type"]
        assert response_json["food_preference"] == new_user_data.food_preference.value
        assert response_json["nutritional_limitations"] == [str(limitation.limitation_id) for limitation in new_user_data.nutritional_limitations]


@pytest.mark.asyncio
async def test_update_user_nutritional_profile_not_found_limitation_id(test_db):
    async with TestClient(app) as client:
        helper_db = TestingSessionLocal()

        user_created = generate_random_user(fake)
        helper_db.add(user_created)

        nutritional_limitation = generate_random_user_nutritional_limitation(fake)
        helper_db.add(nutritional_limitation)
        helper_db.commit()

        new_user_data = generate_random_user(fake)
        new_user_data_json = {
            "food_preference": new_user_data.food_preference.value,
            "nutritional_limitations": [str(nutritional_limitation.limitation_id), str(fake.uuid4())],
        }

        client.headers["user-id"] = str(user_created.user_id)
        response = await client.patch(f"{Constants.USERS_BASE_PATH}/profiles/nutritional", json=new_user_data_json)

        response_json = response.json()

        assert response.status_code == HTTPStatus.NOT_FOUND
        assert Constants.APPLICATION_JSON in response.headers["content-type"]
        assert response_json["message"] == f"Nutritional limitation with id {new_user_data_json['nutritional_limitations'][1]} not found"


@pytest.mark.asyncio
async def test_schedule_premium_sportsman_appointment(test_db):
    async with TestClient(app) as client:
        trainer_id = UUID(fake.uuid4())
        helper_db = TestingSessionLocal()
        trainer = generate_random_trainer(fake)
        trainer.trainer_id = trainer_id
        helper_db.add(trainer)
        helper_db.commit()

        user_created = generate_random_user(fake)
        helper_db.add(user_created)
        helper_db.commit()

        appointment_data = DataClassMapper.to_dict(generate_random_appointment_data(fake, trainer_id), pydantic=True)

        client.headers["user-id"] = str(user_created.user_id)
        response = await client.post(f"{Constants.USERS_BASE_PATH}/premium/sportsman-appointment", json=appointment_data)
        response_json = response.json()
        print(response_json)

        assert response.status_code == HTTPStatus.CREATED
        assert Constants.APPLICATION_JSON in response.headers["content-type"]
        assert "appointment_id" in response_json
        assert "appointment_date" in response_json
        assert response_json["trainer_id"] == str(trainer_id)
        assert response_json["user_id"] == str(user_created.user_id)
        assert response_json["appointment_type"] == appointment_data["appointment_type"]
        assert response_json["appointment_reason"] == appointment_data["appointment_reason"]


@pytest.mark.asyncio
async def test_get_scheduled_premium_appointments(test_db):
    async with TestClient(app) as client:
        trainer_id = UUID(fake.uuid4())
        helper_db = TestingSessionLocal()
        trainer = generate_random_trainer(fake)
        trainer.trainer_id = trainer_id
        helper_db.add(trainer)
        helper_db.commit()

        user_created = generate_random_user(fake)
        helper_db.add(user_created)
        helper_db.commit()

        date_1 = fake.date_time_this_month()
        date_2 = date_1 + timedelta(days=1)

        appointment_1 = generate_random_appointment(fake)
        appointment_1.user_id = user_created.user_id
        appointment_1.trainer_id = trainer_id
        appointment_1.appointment_date = date_1

        appointment_2 = generate_random_appointment(fake)
        appointment_2.user_id = user_created.user_id
        appointment_2.trainer_id = trainer_id
        appointment_2.appointment_date = date_2

        helper_db.add(appointment_1)
        helper_db.add(appointment_2)
        helper_db.commit()

        client.headers["user-id"] = str(user_created.user_id)
        response = await client.get(f"{Constants.USERS_BASE_PATH}/premium/sportsman-appointment")
        response_json = response.json()

        assert response.status_code == HTTPStatus.OK
        assert Constants.APPLICATION_JSON in response.headers["content-type"]
        assert len(response_json) == 2
        assert response_json[0]["appointment_id"] == str(appointment_2.appointment_id)
        assert response_json[0]["appointment_date"] == appointment_2.appointment_date.isoformat()
        assert response_json[0]["trainer_id"] == str(trainer_id)
        assert response_json[0]["appointment_type"] == appointment_2.appointment_type.value
        assert response_json[0]["appointment_reason"] == appointment_2.appointment_reason
        assert response_json[1]["appointment_id"] == str(appointment_1.appointment_id)
        assert response_json[1]["appointment_date"] == appointment_1.appointment_date.isoformat()
        assert response_json[1]["trainer_id"] == str(trainer_id)
        assert response_json[1]["appointment_type"] == appointment_1.appointment_type.value
        assert response_json[1]["appointment_reason"] == appointment_1.appointment_reason


@pytest.mark.asyncio
async def test_get_premium_trainers(test_db):
    async with TestClient(app) as client:
        helper_db = TestingSessionLocal()
        trainer_1 = generate_random_trainer(fake)
        trainer_1.trainer_id = UUID(trainer_1.trainer_id)
        trainer_2 = generate_random_trainer(fake)
        trainer_2.trainer_id = UUID(trainer_2.trainer_id)
        helper_db.add(trainer_1)
        helper_db.add(trainer_2)
        helper_db.commit()

        client.headers["user-id"] = fake.uuid4()
        response = await client.get(f"{Constants.USERS_BASE_PATH}/premium/trainers")
        response_json = response.json()
        print(response_json)

        assert response.status_code == HTTPStatus.OK
        assert Constants.APPLICATION_JSON in response.headers["content-type"]
        assert len(response_json) == 2
        assert response_json[0]["trainer_id"] == str(trainer_1.trainer_id)
        assert response_json[0]["first_name"] == trainer_1.first_name
        assert response_json[0]["last_name"] == trainer_1.last_name
        assert response_json[1]["trainer_id"] == str(trainer_2.trainer_id)
        assert response_json[1]["first_name"] == trainer_2.first_name
        assert response_json[1]["last_name"] == trainer_2.last_name


@pytest.mark.asyncio
async def test_generate_nutritional_plan(test_db, mocker):
    async with TestClient(app) as client:
        helper_db = TestingSessionLocal()
        user_created = generate_random_user(fake)
        helper_db.add(user_created)
        helper_db.commit()

        new_user_data_json = {
            "nutritional_limitations": [],
        }

        external_service_create_nutritional_plan = mocker.patch("app.services.external.ExternalServices.create_nutritional_plan")

        external_service_create_nutritional_plan.return_value = None

        client.headers["user-id"] = str(user_created.user_id)
        response = await client.patch(f"{Constants.USERS_BASE_PATH}/profiles/nutritional", json=new_user_data_json)

        assert response.status_code == HTTPStatus.OK
        assert external_service_create_nutritional_plan.called is True
        assert external_service_create_nutritional_plan.call_count == 1
        assert external_service_create_nutritional_plan.call_args.args[0] == user_created.user_id
        assert external_service_create_nutritional_plan.call_args.args[1]["gender"] == user_created.gender.value
        assert external_service_create_nutritional_plan.call_args.args[1]["training_objective"] == user_created.training_objective.value
        assert external_service_create_nutritional_plan.call_args.args[1]["weight"] == user_created.weight
        assert external_service_create_nutritional_plan.call_args.args[1]["height"] == user_created.height
        assert external_service_create_nutritional_plan.call_args.args[1]["food_preference"] == user_created.food_preference.value
        assert external_service_create_nutritional_plan.call_args.args[1]["nutritional_limitations"] == []
