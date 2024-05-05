import unittest
from unittest.mock import MagicMock, patch
from faker import Faker
from sqlalchemy.orm import Session

from app.models.model import FoodType, FoodTrainingObjective, FoodCategory, Dish, WeekDay
from app.models.schemas.schema import NutritionalPlanCreate, SessionCalories
from app.services.nutritional_plans import NutritionalPlansService
from tests.utils.nutritional_plans_util import generate_random_training_plan_data, generate_random_dishes_data

fake = Faker()


class TestNutritionalPlansService(unittest.TestCase):
    def setUp(self):
        self.mock_db = MagicMock(spec=Session)
        self.sqs_mock = MagicMock()
        self.external_service_mock = MagicMock()
        self.nutritional_plans_service = NutritionalPlansService(db=self.mock_db)
        self.nutritional_plans_service.external_services = self.external_service_mock
        self.nutritional_plans_service.sqs = self.sqs_mock

    def test_create_nutritional_plan_everything(self):
        user_id = fake.uuid4()
        user_auth_token = fake.word()
        training_plan = generate_random_training_plan_data(fake)
        fake_dishes = generate_random_dishes_data(fake, food_type=FoodType.EVERYTHING, objective=FoodTrainingObjective.LOSE_WEIGHT)

        self.external_service_mock.get_training_plan.return_value = training_plan

        nutritional_plan_create = NutritionalPlanCreate(
            age=fake.random_int(min=18, max=45),
            gender=fake.random_element(elements=("F", "M", "O")),
            training_objective=FoodTrainingObjective.LOSE_WEIGHT,
            weight=fake.random_int(min=50, max=100),
            height=fake.pyfloat(min_value=1.5, max_value=2.0),
            food_preference=FoodType.EVERYTHING,
            nutritional_limitations=[fake.word() for _ in range(3)],
        )

        mock_add = MagicMock()
        self.mock_db.add = mock_add
        self.mock_db.query.return_value.filter.return_value.all.return_value = fake_dishes

        self.nutritional_plans_service.create_nutritional_plan(user_id, user_auth_token, nutritional_plan_create)

        # first 5 calls for Monday are just for Intake, because we have 5 dishes already created.
        # Then, next week day calls counts for 10, 1 for intake and 1 for dish (for every FoodType) -> 6 * 10 = 60
        # Total calls = 5 + 60 = 65
        self.assertEqual(mock_add.call_count, 65)

    def test_create_plan_vegan(self):
        user_id = fake.uuid4()
        user_auth_token = fake.word()
        training_plan = generate_random_training_plan_data(fake)
        fake_dishes = generate_random_dishes_data(fake, food_type=FoodType.VEGAN, objective=FoodTrainingObjective.LOSE_WEIGHT)

        self.external_service_mock.get_training_plan.return_value = training_plan

        nutritional_plan_create = NutritionalPlanCreate(
            age=fake.random_int(min=18, max=45),
            gender=fake.random_element(elements=("F", "M", "O")),
            training_objective=FoodTrainingObjective.LOSE_WEIGHT,
            weight=fake.random_int(min=50, max=100),
            height=fake.pyfloat(min_value=1.5, max_value=2.0),
            food_preference=FoodType.VEGAN,
            nutritional_limitations=[fake.word() for _ in range(3)],
        )

        mock_add = MagicMock()
        self.mock_db.add = mock_add
        self.mock_db.query.return_value.filter.return_value.filter.return_value.all.return_value = fake_dishes

        self.nutritional_plans_service.create_nutritional_plan(user_id, user_auth_token, nutritional_plan_create)

        # first 5 calls for Monday are just for Intake, because we have 5 dishes already created.
        # Then, next week day calls counts for 10, 1 for intake and 1 for dish (for every FoodType) -> 6 * 10 = 60
        # Total calls = 5 + 60 = 65
        self.assertEqual(mock_add.call_count, 65)

    def test_create_plan_vegetarian(self):
        user_id = fake.uuid4()
        user_auth_token = fake.word()
        training_plan = generate_random_training_plan_data(fake)
        fake_dishes = generate_random_dishes_data(fake, food_type=FoodType.VEGETARIAN, objective=FoodTrainingObjective.LOSE_WEIGHT)

        self.external_service_mock.get_training_plan.return_value = training_plan

        nutritional_plan_create = NutritionalPlanCreate(
            age=fake.random_int(min=18, max=45),
            gender=fake.random_element(elements=("F", "M", "O")),
            training_objective=FoodTrainingObjective.LOSE_WEIGHT,
            weight=fake.random_int(min=50, max=100),
            height=fake.pyfloat(min_value=1.5, max_value=2.0),
            food_preference=FoodType.VEGETARIAN,
            nutritional_limitations=[fake.word() for _ in range(3)],
        )

        mock_add = MagicMock()
        self.mock_db.add = mock_add
        self.mock_db.query.return_value.filter.return_value.filter.return_value.all.return_value = fake_dishes

        self.nutritional_plans_service.create_nutritional_plan(user_id, user_auth_token, nutritional_plan_create)

        # first 5 calls for Monday are just for Intake, because we have 5 dishes already created.
        # Then, next week day calls counts for 10, 1 for intake and 1 for dish (for every FoodType) -> 6 * 10 = 60
        # Total calls = 5 + 60 = 65
        self.assertEqual(mock_add.call_count, 65)

    def test_notify_positive_message_caloric_intake_lose_weight(self):
        user_id = fake.uuid4()
        user_auth_token = fake.word()

        calories_burn_expected = fake.random_int(min=100, max=500)
        calories_burn = calories_burn_expected + fake.random_int(min=1, max=100)
        session_calories = SessionCalories(calories_burn_expected=calories_burn_expected, calories_burn=calories_burn)

        training_objective = FoodTrainingObjective.LOSE_WEIGHT
        send_message_mock = MagicMock()
        self.sqs_mock.send_message = send_message_mock
        self.external_service_mock.get_user_sport_profile.return_value = {
            "training_objective": training_objective.value,
        }

        fake_recover_snack = Dish(
            food_type=FoodType.EVERYTHING,
            objective=training_objective,
            category=FoodCategory.RECOVERY_SNACK,
            name=fake.word(),
            name_es=fake.word(),
            calories=fake.random_int(min=100, max=500),
            carbs=fake.random_int(min=1, max=100),
            protein=fake.random_int(min=1, max=100),
            fat=fake.random_int(min=1, max=100),
        )
        self.mock_db.query.return_value.join.return_value.filter.return_value.first.return_value = fake_recover_snack

        response = self.nutritional_plans_service.notify_caloric_intake(user_id, user_auth_token, session_calories, "en")

        self.assertEqual(response["user_id"], user_id)
        self.assertEqual(response["message"], "Remember to drink water only to keep your caloric intake low and achieve your goal.")

    def test_notify_positive_message_caloric_intake_lose_weight_spanish(self):
        user_id = fake.uuid4()
        user_auth_token = fake.word()

        calories_burn_expected = fake.random_int(min=100, max=500)
        calories_burn = calories_burn_expected + fake.random_int(min=1, max=100)
        session_calories = SessionCalories(calories_burn_expected=calories_burn_expected, calories_burn=calories_burn)

        training_objective = FoodTrainingObjective.LOSE_WEIGHT
        send_message_mock = MagicMock()
        self.sqs_mock.send_message = send_message_mock
        self.external_service_mock.get_user_sport_profile.return_value = {
            "training_objective": training_objective.value,
        }

        fake_recover_snack = Dish(
            food_type=FoodType.EVERYTHING,
            objective=training_objective,
            category=FoodCategory.RECOVERY_SNACK,
            name=fake.word(),
            name_es=fake.word(),
            calories=fake.random_int(min=100, max=500),
            carbs=fake.random_int(min=1, max=100),
            protein=fake.random_int(min=1, max=100),
            fat=fake.random_int(min=1, max=100),
        )
        self.mock_db.query.return_value.join.return_value.filter.return_value.first.return_value = fake_recover_snack

        response = self.nutritional_plans_service.notify_caloric_intake(user_id, user_auth_token, session_calories, "es")

        self.assertEqual(response["user_id"], user_id)
        self.assertEqual(response["message"], "Recuerda beber solo agua para mantener baja tu ingesta calórica y alcanzar tu objetivo.")

    def test_notify_positive_message_caloric_intake_other(self):
        user_id = fake.uuid4()
        user_auth_token = fake.word()

        calories_burn_expected = fake.random_int(min=100, max=500)
        calories_burn = calories_burn_expected + fake.random_int(min=1, max=100)
        session_calories = SessionCalories(calories_burn_expected=calories_burn_expected, calories_burn=calories_burn)

        training_objective = FoodTrainingObjective.BUILD_MUSCLE_MASS
        send_message_mock = MagicMock()
        self.sqs_mock.send_message = send_message_mock
        self.external_service_mock.get_user_sport_profile.return_value = {
            "training_objective": training_objective.value,
        }

        fake_recover_snack = Dish(
            food_type=FoodType.EVERYTHING,
            objective=training_objective,
            category=FoodCategory.RECOVERY_SNACK,
            name=fake.word(),
            name_es=fake.word(),
            calories=abs(calories_burn_expected - calories_burn) / 2,
            carbs=fake.random_int(min=1, max=100),
            protein=fake.random_int(min=1, max=100),
            fat=fake.random_int(min=1, max=100),
        )
        self.mock_db.query.return_value.join.return_value.filter.return_value.first.return_value = fake_recover_snack

        response = self.nutritional_plans_service.notify_caloric_intake(user_id, user_auth_token, session_calories, "en")

        self.assertEqual(response["user_id"], user_id)
        self.assertEqual(
            response["message"],
            f"Remember to eat 2.0 portions of your recovery snack: {fake_recover_snack.name}. You have {abs(calories_burn_expected - calories_burn)}.0 calories left to consume.",
        )

    def test_notify_positive_message_caloric_intake_other_no_recover_snack(self):
        user_id = fake.uuid4()
        user_auth_token = fake.word()

        calories_burn_expected = fake.random_int(min=100, max=500)
        calories_burn = calories_burn_expected + fake.random_int(min=1, max=100)
        session_calories = SessionCalories(calories_burn_expected=calories_burn_expected, calories_burn=calories_burn)

        training_objective = FoodTrainingObjective.BUILD_MUSCLE_MASS
        send_message_mock = MagicMock()
        self.sqs_mock.send_message = send_message_mock
        self.external_service_mock.get_user_sport_profile.return_value = {
            "training_objective": training_objective.value,
        }

        self.mock_db.query.return_value.join.return_value.filter.return_value.first.return_value = None

        response = self.nutritional_plans_service.notify_caloric_intake(user_id, user_auth_token, session_calories, "en")

        self.assertEqual(response["user_id"], user_id)
        self.assertEqual(response["message"], f"Remember to eat your recovery snack. You have {abs(calories_burn_expected - calories_burn)}.0 calories left to consume.")

    def test_notify_positive_message_caloric_intake_other_spanish(self):
        user_id = fake.uuid4()
        user_auth_token = fake.word()

        calories_burn_expected = fake.random_int(min=100, max=500)
        calories_burn = calories_burn_expected + fake.random_int(min=1, max=100)
        session_calories = SessionCalories(calories_burn_expected=calories_burn_expected, calories_burn=calories_burn)

        training_objective = FoodTrainingObjective.BUILD_MUSCLE_MASS
        send_message_mock = MagicMock()
        self.sqs_mock.send_message = send_message_mock
        self.external_service_mock.get_user_sport_profile.return_value = {
            "training_objective": training_objective.value,
        }

        fake_recover_snack = Dish(
            food_type=FoodType.EVERYTHING,
            objective=training_objective,
            category=FoodCategory.RECOVERY_SNACK,
            name=fake.word(),
            name_es=fake.word(),
            calories=abs(calories_burn_expected - calories_burn) / 2,
            carbs=fake.random_int(min=1, max=100),
            protein=fake.random_int(min=1, max=100),
            fat=fake.random_int(min=1, max=100),
        )
        self.mock_db.query.return_value.join.return_value.filter.return_value.first.return_value = fake_recover_snack

        response = self.nutritional_plans_service.notify_caloric_intake(user_id, user_auth_token, session_calories, "es")

        self.assertEqual(response["user_id"], user_id)
        self.assertEqual(
            response["message"],
            f"Recuerda comer 2.0 porciones de tu snack de recuperación: {fake_recover_snack.name_es}. Te quedan {abs(calories_burn_expected - calories_burn)}.0 calorías por consumir.",
        )

    def test_notify_positive_message_caloric_intake_other_spanish_no_recover_snack(self):
        user_id = fake.uuid4()
        user_auth_token = fake.word()

        calories_burn_expected = fake.random_int(min=100, max=500)
        calories_burn = calories_burn_expected + fake.random_int(min=1, max=100)
        session_calories = SessionCalories(calories_burn_expected=calories_burn_expected, calories_burn=calories_burn)

        training_objective = FoodTrainingObjective.BUILD_MUSCLE_MASS
        send_message_mock = MagicMock()
        self.sqs_mock.send_message = send_message_mock
        self.external_service_mock.get_user_sport_profile.return_value = {
            "training_objective": training_objective.value,
        }
        self.mock_db.query.return_value.join.return_value.filter.return_value.first.return_value = None

        response = self.nutritional_plans_service.notify_caloric_intake(user_id, user_auth_token, session_calories, "es")

        self.assertEqual(response["user_id"], user_id)
        self.assertEqual(response["message"], f"Recuerda comer tu snack de recuperación. Te quedan {abs(calories_burn_expected - calories_burn)}.0 calorías por consumir.")

    def test_notify_negative_message_caloric_intake(self):
        user_id = fake.uuid4()
        user_auth_token = fake.word()

        calories_burn_expected = fake.random_int(min=100, max=500)
        calories_burn = calories_burn_expected - fake.random_int(min=1, max=100)
        session_calories = SessionCalories(calories_burn_expected=calories_burn_expected, calories_burn=calories_burn)

        training_objective = FoodTrainingObjective.LOSE_WEIGHT
        send_message_mock = MagicMock()
        self.sqs_mock.send_message = send_message_mock
        self.external_service_mock.get_user_sport_profile.return_value = {
            "training_objective": training_objective.value,
        }

        response = self.nutritional_plans_service.notify_caloric_intake(user_id, user_auth_token, session_calories, "en")

        self.assertEqual(response["user_id"], user_id)
        self.assertEqual(response["message"], f"Only drink water. You have {calories_burn_expected - calories_burn}.0 left to consume, keep it up!")

    def test_notify_negative_message_caloric_intake_spanish(self):
        user_id = fake.uuid4()
        user_auth_token = fake.word()

        calories_burn_expected = fake.random_int(min=100, max=500)
        calories_burn = calories_burn_expected - fake.random_int(min=1, max=100)
        session_calories = SessionCalories(calories_burn_expected=calories_burn_expected, calories_burn=calories_burn)

        training_objective = FoodTrainingObjective.LOSE_WEIGHT
        send_message_mock = MagicMock()
        self.sqs_mock.send_message = send_message_mock
        self.external_service_mock.get_user_sport_profile.return_value = {
            "training_objective": training_objective.value,
        }

        response = self.nutritional_plans_service.notify_caloric_intake(user_id, user_auth_token, session_calories, "es")

        self.assertEqual(response["user_id"], user_id)
        self.assertEqual(response["message"], f"Solamente bebe agua. Te quedan {calories_burn_expected - calories_burn}.0 para consumir, !sigue así!")

    @patch("app.models.mappers.data_mapper.DataClassMapper.to_dict")
    def test_get_nutritional_plan(self, mock_data_class_mapper):
        user_id = fake.uuid4()

        fake_results = [
            {
                "weekday": fake.enum(WeekDay).value,
                "name": fake.word(),
                "category": fake.enum(FoodCategory).value,
                "calories": fake.random_int(min=100, max=500),
                "carbs": fake.random_int(min=1, max=100),
                "protein": fake.random_int(min=1, max=100),
                "fat": fake.random_int(min=1, max=100),
            }
            for _ in range(5)
        ]
        self.mock_db.query.return_value.join.return_value.filter.return_value.order_by.return_value.all.return_value = fake_results

        mock_data_class_mapper.side_effect = lambda x: x

        response = self.nutritional_plans_service.get_nutritional_plan(user_id, "en")

        self.assertEqual(response, fake_results)

    @patch("app.models.mappers.data_mapper.DataClassMapper.to_dict")
    def test_get_nutritional_plan_spanish(self, mock_data_class_mapper):
        user_id = fake.uuid4()

        fake_results = [
            {
                "weekday": fake.enum(WeekDay).value,
                "name_es": fake.word(),
                "category": fake.enum(FoodCategory).value,
                "calories": fake.random_int(min=100, max=500),
                "carbs": fake.random_int(min=1, max=100),
                "protein": fake.random_int(min=1, max=100),
                "fat": fake.random_int(min=1, max=100),
            }
            for _ in range(5)
        ]
        self.mock_db.query.return_value.join.return_value.filter.return_value.order_by.return_value.all.return_value = fake_results

        mock_data_class_mapper.side_effect = lambda x: x

        response = self.nutritional_plans_service.get_nutritional_plan(user_id, "es")

        self.assertEqual(response, fake_results)
