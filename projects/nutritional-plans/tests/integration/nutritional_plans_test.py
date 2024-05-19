from uuid import UUID

import faker
import pytest
from fastapi.testclient import TestClient
from mock.mock import MagicMock
from sqlalchemy import create_engine, StaticPool
from sqlalchemy.orm import sessionmaker

from app.models.model import FoodType, FoodTrainingObjective, Dish, FoodIntake, FoodCategory, WeekDay
from main import app
from app.config.db import base, get_db
from tests.utils.nutritional_plans_util import generate_random_dishes_data, generate_random_training_plan_data


class Constants:
    SPORT_EVENTS_BASE_PATH = "/nutritional-plans"
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
user_id = fake.uuid4()
client.headers = {"user-id": str(user_id)}


@pytest.fixture()
def test_db():
    base.metadata.create_all(bind=test_engine)
    yield
    base.metadata.drop_all(bind=test_engine)


@pytest.mark.asyncio
def test_create_nutritional_plan(test_db, mocker):
    helper_db = TestingSessionLocal()
    dishes = generate_random_dishes_data(fake, FoodType.EVERYTHING, FoodTrainingObjective.BUILD_MUSCLE_MASS)
    helper_db.add_all(dishes)
    helper_db.commit()

    external_service_get_training_plan = mocker.patch("app.services.external.ExternalServices.get_training_plan")
    external_service_get_training_plan.return_value = generate_random_training_plan_data(fake)

    response = client.post(
        f"{Constants.SPORT_EVENTS_BASE_PATH}/",
        json={
            "age": 25,
            "gender": "M",
            "training_objective": FoodTrainingObjective.BUILD_MUSCLE_MASS.value,
            "weight": 80.0,
            "height": 1.8,
            "food_preference": FoodType.EVERYTHING.value,
            "nutritional_limitations": [],
        },
    )

    response_json = response.json()

    dishes = helper_db.query(Dish).all()
    food_intakes = helper_db.query(FoodIntake).all()

    assert response.status_code == 201
    assert response_json["user_id"] == str(user_id)
    assert response_json["message"] == "Nutritional plan created successfully"

    # 7 days * 5 meals each day = 35 dishes
    assert len(dishes) == 35
    # 7 days * 5 food intakes each day = 35 food intakes
    assert len(food_intakes) == 35


@pytest.mark.asyncio
def test_positive_notification_caloric_intake_lose_weight(test_db, mocker):
    calories_burn_expected = fake.random_int(min=1, max=1000)
    calories_burn = calories_burn_expected + fake.random_int(min=1, max=100)

    external_service_get_sports_profile = mocker.patch("app.services.external.ExternalServices.get_user_sport_profile")
    external_service_get_sports_profile.return_value = {
        "training_objective": FoodTrainingObjective.LOSE_WEIGHT.value,
    }

    boto3_session = mocker.patch("boto3.Session")
    send_message_mock = MagicMock()
    boto3_session.client.return_value.send_message.return_value = send_message_mock

    response = client.post(
        f"{Constants.SPORT_EVENTS_BASE_PATH}/notify-caloric-intake",
        json={
            "calories_burn_expected": calories_burn_expected,
            "calories_burn": calories_burn,
        },
    )

    response_json = response.json()

    assert response.status_code == 200
    assert response_json["user_id"] == str(user_id)
    assert response_json["message"] == "Remember to drink water only to keep your caloric intake low and achieve your goal."


@pytest.mark.asyncio
def test_positive_notification_caloric_intake_lose_weight_spanish(test_db, mocker):
    calories_burn_expected = fake.random_int(min=1, max=1000)
    calories_burn = calories_burn_expected + fake.random_int(min=1, max=100)

    external_service_get_sports_profile = mocker.patch("app.services.external.ExternalServices.get_user_sport_profile")
    external_service_get_sports_profile.return_value = {
        "training_objective": FoodTrainingObjective.LOSE_WEIGHT.value,
    }

    boto3_session = mocker.patch("boto3.Session")
    send_message_mock = MagicMock()
    boto3_session.client.return_value.send_message.return_value = send_message_mock

    response = client.post(
        f"{Constants.SPORT_EVENTS_BASE_PATH}/notify-caloric-intake?lang=es",
        json={
            "calories_burn_expected": calories_burn_expected,
            "calories_burn": calories_burn,
        },
    )

    response_json = response.json()

    assert response.status_code == 200
    assert response_json["user_id"] == str(user_id)
    assert response_json["message"] == "Recuerda beber solo agua para mantener baja tu ingesta calórica y alcanzar tu objetivo."


@pytest.mark.asyncio
def test_negative_notification_caloric_intake_lose_weight(test_db, mocker):
    calories_burn_expected = fake.random_int(min=1, max=1000)
    calories_burn = calories_burn_expected - fake.random_int(min=1, max=100)

    external_service_get_sports_profile = mocker.patch("app.services.external.ExternalServices.get_user_sport_profile")
    external_service_get_sports_profile.return_value = {
        "training_objective": FoodTrainingObjective.LOSE_WEIGHT.value,
    }

    boto3_session = mocker.patch("boto3.Session")
    send_message_mock = MagicMock()
    boto3_session.client.return_value.send_message.return_value = send_message_mock

    response = client.post(
        f"{Constants.SPORT_EVENTS_BASE_PATH}/notify-caloric-intake",
        json={
            "calories_burn_expected": calories_burn_expected,
            "calories_burn": calories_burn,
        },
    )

    response_json = response.json()

    assert response.status_code == 200
    assert response_json["user_id"] == str(user_id)
    assert response_json["message"] == f"Only drink water. You have {abs(calories_burn_expected - calories_burn)}.0 left to consume, keep it up!"


@pytest.mark.asyncio
def test_negative_notification_caloric_intake_lose_weight_spanish(test_db, mocker):
    calories_burn_expected = fake.random_int(min=1, max=1000)
    calories_burn = calories_burn_expected - fake.random_int(min=1, max=100)

    external_service_get_sports_profile = mocker.patch("app.services.external.ExternalServices.get_user_sport_profile")
    external_service_get_sports_profile.return_value = {
        "training_objective": FoodTrainingObjective.LOSE_WEIGHT.value,
    }

    boto3_session = mocker.patch("boto3.Session")
    send_message_mock = MagicMock()
    boto3_session.client.return_value.send_message.return_value = send_message_mock

    response = client.post(
        f"{Constants.SPORT_EVENTS_BASE_PATH}/notify-caloric-intake?lang=es",
        json={
            "calories_burn_expected": calories_burn_expected,
            "calories_burn": calories_burn,
        },
    )

    response_json = response.json()

    assert response.status_code == 200
    assert response_json["user_id"] == str(user_id)
    assert response_json["message"] == f"Solamente bebe agua. Te quedan {abs(calories_burn_expected - calories_burn)}.0 para consumir, !sigue así!"


@pytest.mark.asyncio
def test_positive_notification_caloric_intake_other(test_db, mocker):
    helper_db = TestingSessionLocal()

    calories_burn_expected = fake.random_int(min=1, max=1000)
    calories_burn = calories_burn_expected + fake.random_int(min=1, max=100)

    dish_id = UUID(fake.uuid4())
    snack = Dish(
        dish_id=dish_id,
        name="Recovery Snack",
        name_es="Merienda de recuperación",
        calories=abs(calories_burn_expected - calories_burn) / 2,
        carbs=10,
        protein=20,
        fat=20,
        food_type=FoodType.EVERYTHING,
        category=FoodCategory.RECOVERY_SNACK,
        objective=FoodTrainingObjective.BUILD_MUSCLE_MASS,
    )
    helper_db.add(snack)
    helper_db.commit()

    weekday = WeekDay.MONDAY
    mock_datetime = mocker.patch("app.utils.utils.datetime")
    mock_datetime.now.return_value.weekday.return_value = 0  # Monday

    food_intake = FoodIntake(
        user_id=UUID(user_id),
        week_day=weekday,
        dish_id=snack.dish_id,
    )

    helper_db.add(food_intake)
    helper_db.commit()

    external_service_get_sports_profile = mocker.patch("app.services.external.ExternalServices.get_user_sport_profile")
    external_service_get_sports_profile.return_value = {
        "training_objective": FoodTrainingObjective.BUILD_MUSCLE_MASS.value,
    }

    boto3_session = mocker.patch("boto3.Session")
    send_message_mock = MagicMock()
    boto3_session.client.return_value.send_message.return_value = send_message_mock

    response = client.post(
        f"{Constants.SPORT_EVENTS_BASE_PATH}/notify-caloric-intake",
        json={
            "calories_burn_expected": calories_burn_expected,
            "calories_burn": calories_burn,
        },
    )

    response_json = response.json()

    assert response.status_code == 200
    assert response_json["user_id"] == str(user_id)
    assert (
        response_json["message"]
        == f"Remember to eat 2.0 portions of your recovery snack: {snack.name}. You have {abs(calories_burn_expected - calories_burn)}.0 calories left to consume."
    )


@pytest.mark.asyncio
def test_positive_notification_caloric_intake_other_spanish(test_db, mocker):
    helper_db = TestingSessionLocal()

    calories_burn_expected = fake.random_int(min=1, max=1000)
    calories_burn = calories_burn_expected + fake.random_int(min=1, max=100)

    dish_id = UUID(fake.uuid4())
    snack = Dish(
        dish_id=dish_id,
        name="Recovery Snack",
        name_es="Merienda de recuperación",
        calories=abs(calories_burn_expected - calories_burn) / 2,
        carbs=10,
        protein=20,
        fat=20,
        food_type=FoodType.EVERYTHING,
        category=FoodCategory.RECOVERY_SNACK,
        objective=FoodTrainingObjective.BUILD_MUSCLE_MASS,
    )
    helper_db.add(snack)
    helper_db.commit()

    weekday = WeekDay.MONDAY
    mock_datetime = mocker.patch("app.utils.utils.datetime")
    mock_datetime.now.return_value.weekday.return_value = 0  # Monday

    food_intake = FoodIntake(
        user_id=UUID(user_id),
        week_day=weekday,
        dish_id=snack.dish_id,
    )

    helper_db.add(food_intake)
    helper_db.commit()

    external_service_get_sports_profile = mocker.patch("app.services.external.ExternalServices.get_user_sport_profile")
    external_service_get_sports_profile.return_value = {
        "training_objective": FoodTrainingObjective.BUILD_MUSCLE_MASS.value,
    }

    boto3_session = mocker.patch("boto3.Session")
    send_message_mock = MagicMock()
    boto3_session.client.return_value.send_message.return_value = send_message_mock

    response = client.post(
        f"{Constants.SPORT_EVENTS_BASE_PATH}/notify-caloric-intake?lang=es",
        json={
            "calories_burn_expected": calories_burn_expected,
            "calories_burn": calories_burn,
        },
    )

    response_json = response.json()

    assert response.status_code == 200
    assert response_json["user_id"] == str(user_id)
    assert (
        response_json["message"]
        == f"Recuerda comer 2.0 porciones de tu snack de recuperación: {snack.name_es}. Te quedan {abs(calories_burn_expected - calories_burn)}.0 calorías por consumir."
    )


@pytest.mark.asyncio
def test_positive_notification_caloric_intake_other_no_snack(test_db, mocker):
    calories_burn_expected = fake.random_int(min=1, max=1000)
    calories_burn = calories_burn_expected + fake.random_int(min=1, max=100)

    external_service_get_sports_profile = mocker.patch("app.services.external.ExternalServices.get_user_sport_profile")
    external_service_get_sports_profile.return_value = {
        "training_objective": FoodTrainingObjective.BUILD_MUSCLE_MASS.value,
    }

    boto3_session = mocker.patch("boto3.Session")
    send_message_mock = MagicMock()
    boto3_session.client.return_value.send_message.return_value = send_message_mock

    response = client.post(
        f"{Constants.SPORT_EVENTS_BASE_PATH}/notify-caloric-intake",
        json={
            "calories_burn_expected": calories_burn_expected,
            "calories_burn": calories_burn,
        },
    )

    response_json = response.json()

    assert response.status_code == 200
    assert response_json["user_id"] == str(user_id)
    assert response_json["message"] == f"Remember to eat your recovery snack. You have {abs(calories_burn_expected - calories_burn)}.0 calories left to consume."


@pytest.mark.asyncio
def test_positive_notification_caloric_intake_other_no_snack_spanish(test_db, mocker):
    calories_burn_expected = fake.random_int(min=1, max=1000)
    calories_burn = calories_burn_expected + fake.random_int(min=1, max=100)

    external_service_get_sports_profile = mocker.patch("app.services.external.ExternalServices.get_user_sport_profile")
    external_service_get_sports_profile.return_value = {
        "training_objective": FoodTrainingObjective.BUILD_MUSCLE_MASS.value,
    }

    boto3_session = mocker.patch("boto3.Session")
    send_message_mock = MagicMock()
    boto3_session.client.return_value.send_message.return_value = send_message_mock

    response = client.post(
        f"{Constants.SPORT_EVENTS_BASE_PATH}/notify-caloric-intake?lang=es",
        json={
            "calories_burn_expected": calories_burn_expected,
            "calories_burn": calories_burn,
        },
    )

    response_json = response.json()

    assert response.status_code == 200
    assert response_json["user_id"] == str(user_id)
    assert response_json["message"] == f"Recuerda comer tu snack de recuperación. Te quedan {abs(calories_burn_expected - calories_burn)}.0 calorías por consumir."
