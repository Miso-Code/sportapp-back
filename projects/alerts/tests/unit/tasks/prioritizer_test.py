import unittest
from unittest.mock import patch, MagicMock

from app.tasks.prioritizer import QueueProcessor


class TestQueueProcessor(unittest.TestCase):

    @patch("app.tasks.publisher.Publisher.send_alert")
    def test_process_queues(self, publisher_mock):
        self.sqs_mock = MagicMock()
        self.processor = QueueProcessor()
        self.processor.sqs = self.sqs_mock

        self.sqs_mock.get_messages.side_effect = [
            {"Messages": [{"Body": '{"user_id": "123", "message": "Test message"}'}]},
            {"Messages": [{"Body": '{"user_id": "456", "message": "Test message"}'}]},
        ]

        publisher_mock.side_effect = lambda *args, **kwargs: self.processor.stop_processing()

        self.processor.process_queues()

        self.assertEqual(self.sqs_mock.get_messages.call_count, 2)

    @patch("app.tasks.publisher.Publisher.send_alert")
    def test_process_queues_no_messages(self, publisher_mock):
        self.sqs_mock = MagicMock()
        self.processor = QueueProcessor()
        self.processor.sqs = self.sqs_mock

        self.sqs_mock.get_messages.side_effect = lambda *args, **kwargs: self.processor.stop_processing()

        self.processor.process_queues()

        self.assertEqual(self.sqs_mock.get_messages.call_count, 2)
        publisher_mock.assert_not_called()

    @patch("app.tasks.publisher.Publisher.send_alert")
    def test_process_queues_error(self, publisher_mock):
        self.sqs_mock = MagicMock()
        self.processor = QueueProcessor()
        self.processor.sqs = self.sqs_mock

        self.sqs_mock.get_messages.side_effect = [
            {"Messages": [{"Body": '{"user_id": "123", "message": "Test message"}'}]},
            Exception("Error getting messages"),
        ]

        publisher_mock.side_effect = lambda *args, **kwargs: self.processor.stop_processing()
        self.sqs_mock.delete_message.side_effect = Exception("Error deleting message")

        self.processor.process_queues()

        self.assertEqual(self.sqs_mock.get_messages.call_count, 1)
        publisher_mock.assert_called_once()
