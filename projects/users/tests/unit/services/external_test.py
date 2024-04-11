import unittest

from unittest.mock import patch

from faker import Faker
from app.services.external import ExternalServices
from app.exceptions.exceptions import NotFoundError

fake = Faker()


class TestExternalService(unittest.TestCase):

    @patch("requests.get")
    def test_get_sport(self, mock_get):
        user_id = fake.uuid4()
        external_service = ExternalServices()
        mock_get.return_value.status_code = 200
        mock_get.return_value.json.return_value = {"id": user_id}

        response = external_service.get_sport(user_id)

        self.assertEqual(response, {"id": user_id})
        self.assertTrue(mock_get.called)

    @patch("requests.get")
    def test_get_sport_not_found(self, mock_get):
        user_id = fake.uuid4()
        external_service = ExternalServices()
        mock_get.return_value.status_code = 404

        with self.assertRaises(NotFoundError) as context:
            external_service.get_sport(user_id)

        self.assertEqual(str(context.exception), f"Sport with id {user_id} not found")
