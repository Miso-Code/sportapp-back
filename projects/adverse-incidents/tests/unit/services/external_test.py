import unittest

from unittest.mock import patch

from faker import Faker

from app.exceptions.exceptions import ExternalServiceError
from app.services.external import ExternalServices

fake = Faker()


class TestExternalService(unittest.TestCase):

    @patch("requests.post")
    def test_get_incidents(self, mock_post):
        mock_post.return_value.status_code = 200
        mock_post.return_value.json.return_value = [{"id": fake.uuid4()}]
        external_service = ExternalServices()
        incidents = external_service.get_incidents()
        self.assertEqual(len(incidents), 1)

    @patch("requests.post")
    def test_get_incidents_error(self, mock_post):
        mock_post.return_value.status_code = 500
        external_service = ExternalServices()
        with self.assertRaises(ExternalServiceError) as context:
            external_service.get_incidents()
        self.assertTrue("Failed to get incidents" in str(context.exception))

    @patch("requests.get")
    def test_get_users_training(self, mock_get):
        mock_get.return_value.status_code = 200
        mock_get.return_value.json.return_value = [{"id": fake.uuid4()}]
        external_service = ExternalServices()
        users_training = external_service.get_users_training()
        self.assertEqual(len(users_training), 1)

    @patch("requests.get")
    def test_get_users_training_error(self, mock_get):
        mock_get.return_value.status_code = 500
        external_service = ExternalServices()
        with self.assertRaises(ExternalServiceError) as context:
            external_service.get_users_training()
        self.assertTrue("Failed to get users training" in str(context.exception))
