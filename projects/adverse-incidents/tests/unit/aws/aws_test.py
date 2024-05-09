import unittest
from unittest.mock import MagicMock

from app.aws.aws import AWSClient, SQS


class TestSQS(unittest.TestCase):
    def setUp(self):
        mock_session = MagicMock()
        self.mock_client = MagicMock()
        self.mock_session = mock_session
        mock_session.client.return_value = self.mock_client
        self.sqs = SQS(self.mock_session)

    def test_send_message(self):
        self.mock_client.send_message.return_value = {"MessageId": "test_message_id"}

        queue_name = "test_queue_name"
        message = "test_message"

        self.sqs.send_message(queue_name, message)

        self.mock_client.send_message.assert_called_once_with(QueueUrl=queue_name, MessageBody=message, MessageGroupId="nutritional_plan")


class TestAWSClient(unittest.TestCase):
    def test_aws_client_initialization(self):
        aws_client = AWSClient()

        self.assertIsNotNone(aws_client.sqs)
        self.assertIsInstance(aws_client.sqs, SQS)
