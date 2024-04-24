import unittest
from app.models.training_plan import TrainingPlanSession
from faker import Faker

fake = Faker()


class TestTrainingPlan(unittest.TestCase):
    def test_training_plan_creation(self):
        training_plan_session_data = {
            "training_plan_session_id": fake.uuid4(),
            "weekday": fake.day_of_week().lower(),
            "start_time": fake.time(pattern="%I:%M %p"),
            "warm_up": fake.random_int(min=1, max=10),
            "cardio": fake.random_int(min=1, max=10),
            "strength": fake.random_int(min=1, max=10),
            "cool_down": fake.random_int(min=1, max=10),
            "user_id": fake.uuid4(),
        }

        training_plan_session = TrainingPlanSession(**training_plan_session_data)

        self.assertEqual(training_plan_session.training_plan_session_id, training_plan_session_data["training_plan_session_id"])
        self.assertEqual(training_plan_session.weekday, training_plan_session_data["weekday"])
        self.assertEqual(training_plan_session.start_time, training_plan_session_data["start_time"])
        self.assertEqual(training_plan_session.warm_up, training_plan_session_data["warm_up"])
        self.assertEqual(training_plan_session.cardio, training_plan_session_data["cardio"])
        self.assertEqual(training_plan_session.strength, training_plan_session_data["strength"])
        self.assertEqual(training_plan_session.cool_down, training_plan_session_data["cool_down"])
        self.assertEqual(training_plan_session.user_id, training_plan_session_data["user_id"])
