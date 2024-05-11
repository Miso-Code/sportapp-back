import unittest
from unittest.mock import MagicMock

from botocore.exceptions import ClientError
from faker import Faker

from app.exceptions.exceptions import ExternalServiceError
from app.services.adverse_incidents import AdverseIncidentsService
from tests.utils.processor_test_util import generate_random_incidents, generate_random_users_training

fake = Faker()


class TestAdverseIncidentsService(unittest.TestCase):
    def setUp(self):
        self.mock_sqs = MagicMock()
        self.mock_external_services = MagicMock()
        self.mock_adverse_incidents_queue_name = fake.word()
        self.adverse_incidents_service = AdverseIncidentsService()
        self.adverse_incidents_service.sqs = self.mock_sqs
        self.adverse_incidents_service.external_services = self.mock_external_services

    def test_process_incidents(self):
        # Generate 3 random incidents
        fake_incidents = generate_random_incidents(fake)
        fake_users_training = generate_random_users_training(fake, fake_incidents, 2)

        self.mock_external_services.get_incidents.return_value = fake_incidents
        self.mock_external_services.get_users_training.return_value = fake_users_training
        self.mock_sqs.send_message.return_value = None

        response = self.adverse_incidents_service.process_incidents()

        # 6 Users were notified because there are 3 incidents and each incident has 2 users in the bounding box
        self.assertEqual(response["message"], f"Processed {len(fake_incidents)} incidents and notified 6 users.")
        self.mock_external_services.get_incidents.assert_called_once()
        self.mock_external_services.get_users_training.assert_called_once()
        self.assertEqual(self.mock_sqs.send_message.call_count, 6)

    def test_process_incidents_external_service_error(self):
        self.mock_external_services.get_incidents.side_effect = ExternalServiceError("Error")
        response = self.adverse_incidents_service.process_incidents()
        self.assertEqual(response["message"], "Failed to process incidents: Error")

    def test_process_incidents_aws_client_error(self):
        fake_incidents = generate_random_incidents(fake)
        fake_users_training = generate_random_users_training(fake, fake_incidents, 2)

        self.mock_external_services.get_incidents.return_value = fake_incidents
        self.mock_external_services.get_users_training.return_value = fake_users_training
        self.mock_sqs.send_message.side_effect = ClientError({"Error": {"Code": "TestCode", "Message": "TestMessage"}}, "send_message")

        response = self.adverse_incidents_service.process_incidents()

        self.assertEqual(response["message"], "Error processing incidents: An error occurred (TestCode) when calling the send_message operation: TestMessage")
