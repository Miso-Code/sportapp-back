import unittest
from logging import Logger
from unittest.mock import patch, MagicMock

import faker

from app.tasks.processor import Processor

fake = faker.Faker()


class TestProcessor(unittest.TestCase):

    def setUp(self):
        self.logger = MagicMock(spec=Logger)
        self.adverse_incidents_service_mock = MagicMock()
        self.processor = Processor(logger=self.logger)
        self.processor.adverse_incidents_service = self.adverse_incidents_service_mock

    @patch("app.tasks.processor.sleep")
    @patch("app.tasks.processor.Config.NOTIFIER_SLEEP_TIME_SECONDS", 60)
    def test_process_incidents(self, mock_sleep):
        mock_process_incidents_return = "Incidents processed successfully"
        self.adverse_incidents_service_mock.process_incidents.return_value = mock_process_incidents_return

        mock_sleep.side_effect = lambda *args, **kwargs: self.processor.stop_processing()

        self.processor.process_incidents()
        self.logger.info.assert_called_once_with(mock_process_incidents_return)
        self.logger.warning.assert_called_once_with("Waiting 60 seconds before processing next incidents")

    @patch("app.tasks.processor.sleep")
    @patch("app.tasks.processor.Config.NOTIFIER_SLEEP_TIME_SECONDS", 60)
    def test_process_incidents_exception(self, mock_sleep):
        self.adverse_incidents_service_mock.process_incidents.side_effect = Exception("Something went wrong")

        mock_sleep.side_effect = lambda *args, **kwargs: self.processor.stop_processing()

        self.processor.process_incidents()
        self.logger.error.assert_called_once()
        self.logger.warning.assert_called_once_with("Waiting 60 seconds before processing next incidents")
