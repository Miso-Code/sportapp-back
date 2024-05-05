import json
import unittest

from unittest.mock import patch, MagicMock

from faker import Faker

from app.models.model import FoodTrainingObjective, FoodType
from app.models.schemas.schema import NutritionalPlanCreate, SessionCalories
from app.routes import nutritional_plans_routes

fake = Faker()


class TestNutritionalPlansRoutes(unittest.IsolatedAsyncioTestCase):

    @patch("app.services.nutritional_plans.NutritionalPlansService.create_nutritional_plan")
    async def test_create_nutritional_plan(self, mock_create_nutritional_plan):
        mock_create_nutritional_plan.return_value = {"user_id": fake.uuid4(), "message": fake.text()}
        user_id = fake.uuid4()
        nutritional_plan_create = NutritionalPlanCreate(
            age=fake.random_int(min=18, max=45),
            gender=fake.random_element(elements=("F", "M", "O")),
            training_objective=FoodTrainingObjective.LOSE_WEIGHT,
            weight=fake.random_int(min=50, max=100),
            height=fake.pyfloat(min_value=1.5, max_value=2.0),
            food_preference=FoodType.EVERYTHING,
            nutritional_limitations=[fake.word() for _ in range(3)],
        )
        authorization = fake.text()
        db = MagicMock()
        message = fake.text()

        mock_create_nutritional_plan.return_value = {"user_id": user_id, "message": message}

        response = await nutritional_plans_routes.create_nutritional_plan(user_id, nutritional_plan_create, authorization, db)
        response_json = json.loads(response.body)

        self.assertEqual(response.status_code, 201)
        self.assertEqual(response_json["user_id"], user_id)
        self.assertEqual(response_json["message"], message)

    @patch("app.services.nutritional_plans.NutritionalPlansService.get_nutritional_plan")
    async def test_get_nutritional_plan(self, mock_get_nutritional_plan):
        mock_get_nutritional_plan.return_value = {"user_id": fake.uuid4(), "message": fake.text()}
        user_id = fake.uuid4()
        lang = fake.word()
        db = MagicMock()
        message = fake.text()

        mock_get_nutritional_plan.return_value = {"user_id": user_id, "message": message}

        response = await nutritional_plans_routes.get_nutritional_plan(user_id, lang, db)
        response_json = json.loads(response.body)

        self.assertEqual(response.status_code, 200)
        self.assertEqual(response_json["user_id"], user_id)
        self.assertEqual(response_json["message"], message)

    @patch("app.services.nutritional_plans.NutritionalPlansService.notify_caloric_intake")
    async def test_notify_caloric_intake(self, mock_notify_caloric_intake):
        mock_notify_caloric_intake.return_value = {"user_id": fake.uuid4(), "message": fake.text()}
        user_id = fake.uuid4()
        calories_burn_expected = fake.random_int(min=100, max=500)
        calories_burn = calories_burn_expected + fake.random_int(min=1, max=100)
        session_calories = SessionCalories(calories_burn_expected=calories_burn_expected, calories_burn=calories_burn)
        lang = fake.word()
        authorization = fake.text()
        db = MagicMock()
        message = fake.text()

        mock_notify_caloric_intake.return_value = {"user_id": user_id, "message": message}

        response = await nutritional_plans_routes.notify_caloric_intake(session_calories, user_id, lang, authorization, db)
        response_json = json.loads(response.body)

        self.assertEqual(response.status_code, 200)
        self.assertEqual(response_json["user_id"], user_id)
        self.assertEqual(response_json["message"], message)
