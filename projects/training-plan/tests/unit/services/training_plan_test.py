import unittest

from unittest.mock import MagicMock, patch

from faker import Faker
from sqlalchemy.orm import Session

from app.models.mappers.training_plan_mapper import DataClassMapper
from app.services.training_plan import TrainingPlanService

from tests.utils.training_plan_utils import generate_random_training_plan_create_data, generate_random_training_plan_session_dict

fake = Faker()


class TestTrainingPlanService(unittest.TestCase):
    def setUp(self):
        self.mock_db = MagicMock(spec=Session)
        self.training_plan_service = TrainingPlanService(db=self.mock_db)

    @patch("app.models.mappers.training_plan_mapper.DataClassMapper.to_dict")
    def test_create_training_plan(self, mock_to_dict):
        training_plan_data = generate_random_training_plan_create_data(fake)
        user_id = fake.uuid4()

        training_plan_session = generate_random_training_plan_session_dict(fake)

        mock_to_dict.return_value = training_plan_session

        self.training_plan_service.generate_training_plan(user_id, training_plan_data)

        self.assertEqual(self.mock_db.query.call_count, 1)
        self.assertEqual(self.mock_db.commit.call_count, 1)
        self.assertEqual(self.mock_db.add.call_count, len(training_plan_data.available_weekdays))
        self.assertEqual(self.mock_db.refresh.call_count, len(training_plan_data.available_weekdays))

    @patch("app.models.mappers.training_plan_mapper.DataClassMapper.to_dict")
    def test_get_training_plan(self, mock_to_dict):
        user_id = fake.uuid4()

        training_plan_session = generate_random_training_plan_session_dict(fake)

        self.mock_db.query.return_value.filter.return_value.all.return_value = [training_plan_session]
        mock_to_dict.return_value = training_plan_session

        response = self.training_plan_service.get_training_plan(user_id)

        self.assertEqual(self.mock_db.query.call_count, 1)
        self.assertEqual(response, [training_plan_session])
