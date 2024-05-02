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

    def test_receive_message(self):
        self.mock_client.receive_message.return_value = {"Messages": [{"Body": "test_body"}]}

        queue_name = "test_queue_name"

        messages = self.sqs.get_messages(queue_name)

        self.assertEqual(messages, {"Messages": [{"Body": "test_body"}]})
        self.mock_client.receive_message.assert_called_once_with(QueueUrl=queue_name)

    def test_delete_message(self):
        message = {"ReceiptHandle": "test_receipt_handle"}

        queue_name = "test_queue_name"

        self.sqs.delete_message(queue_name, message)

        self.mock_client.delete_message.assert_called_once_with(QueueUrl=queue_name, ReceiptHandle=message["ReceiptHandle"])
        print(f"Message deleted from {queue_name}")


class TestAWSClient(unittest.TestCase):
    def test_aws_client_initialization(self):
        aws_client = AWSClient()

        self.assertIsNotNone(aws_client.sqs)
        self.assertIsInstance(aws_client.sqs, SQS)
