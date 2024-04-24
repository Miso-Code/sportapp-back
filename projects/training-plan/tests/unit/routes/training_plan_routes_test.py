import json
import unittest

from unittest.mock import patch, MagicMock

from faker import Faker

from app.models.schemas.schema import TrainingPlanCreate, TrainingObjective
from app.routes import training_plan_routes
from tests.utils.training_plan_utils import generate_random_training_plan_session_dict

fake = Faker()


class TestTrainingPlanRoutes(unittest.IsolatedAsyncioTestCase):

    @patch("app.services.training_plan.TrainingPlanService.generate_training_plan")
    async def test_create_training_plan(self, generate_training_plan_mock):
        training_objective = fake.random.choice(list(TrainingObjective))
        available_training_hours = fake.random_int(min=1, max=24)
        available_weekdays = list(set([fake.day_of_week().lower() for _ in range(fake.random_int(min=1, max=7))]))
        preferred_training_start_time = fake.time(pattern="%I:%M %p")
        favourite_sport_id = fake.uuid4()
        weight = fake.random_int(min=1, max=200)
        height = fake.random_int(min=1, max=200)
        training_limitations = [{"name": fake.word(), "description": fake.sentence()} for _ in range(fake.random_int(min=1, max=5))]

        training_plan_data = {
            "training_objective": training_objective,
            "available_training_hours": available_training_hours,
            "available_weekdays": available_weekdays,
            "preferred_training_start_time": preferred_training_start_time,
            "favourite_sport_id": favourite_sport_id,
            "weight": weight,
            "height": height,
            "training_limitations": training_limitations,
        }
        training_plan_create = TrainingPlanCreate(**training_plan_data)

        db = MagicMock()

        training_plan_sessions = [generate_random_training_plan_session_dict(fake) for _ in range(fake.random_int(min=1, max=7))]

        generate_training_plan_mock.return_value = training_plan_sessions

        user_id = fake.uuid4()

        response = await training_plan_routes.create_training_plan(training_plan_create, user_id, db)
        response_body = json.loads(response.body)

        self.assertEqual(response.status_code, 200)
        generate_training_plan_mock.assert_called_once_with(user_id, training_plan_create)
        self.assertEqual(response_body, training_plan_sessions)

    @patch("app.services.training_plan.TrainingPlanService.get_training_plan")
    async def test_get_training_plan(self, get_training_plan_mock):
        db = MagicMock()

        training_plan_sessions = [generate_random_training_plan_session_dict(fake) for _ in range(fake.random_int(min=1, max=7))]

        user_id = fake.uuid4()

        get_training_plan_mock.return_value = training_plan_sessions

        response = await training_plan_routes.get_training_plan(user_id, db)
        response_body = json.loads(response.body)

        self.assertEqual(response.status_code, 200)
        get_training_plan_mock.assert_called_once_with(user_id)
        self.assertEqual(response_body, training_plan_sessions)
