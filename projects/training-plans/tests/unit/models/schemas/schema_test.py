import unittest

from faker import Faker
from pydantic import ValidationError

from app.models.schemas.schema import TrainingPlanCreate, TrainingObjective

fake = Faker()


class TestUserCreate(unittest.TestCase):
    def test_valid_training_plan_create(self):
        training_objective = fake.random.choice(list(TrainingObjective))
        available_weekdays = list({fake.day_of_week().lower(), fake.day_of_week().lower(), fake.day_of_week().lower()})
        preferred_training_start_time = fake.time(pattern="%I:%M %p")
        available_training_hours = fake.random_int(min=1, max=10)

        training_plan_data = {
            "training_objective": training_objective,
            "available_weekdays": available_weekdays,
            "preferred_training_start_time": preferred_training_start_time,
            "available_training_hours": available_training_hours,
        }

        training_plan = TrainingPlanCreate(**training_plan_data)
        self.assertEqual(training_plan.training_objective, training_objective)
        self.assertEqual(training_plan.available_weekdays, set(available_weekdays))
        self.assertEqual(training_plan.preferred_training_start_time, preferred_training_start_time)
        self.assertEqual(training_plan.available_training_hours, available_training_hours)

    def test_invalid_training_plan_create(self):
        training_objective = fake.word()
        available_weekdays = [fake.word(), fake.word(), fake.word()]
        preferred_training_start_time = fake.word()
        available_training_hours = fake.word()

        training_plan_data = {
            "training_objective": training_objective,
            "available_weekdays": available_weekdays,
            "preferred_training_start_time": preferred_training_start_time,
            "available_training_hours": available_training_hours,
        }

        with self.assertRaises(ValidationError):
            TrainingPlanCreate(**training_plan_data)
