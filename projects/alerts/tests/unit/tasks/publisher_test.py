import unittest
from unittest.mock import patch, MagicMock

import faker

from app.tasks.publisher import Publisher

fake = faker.Faker()


class TestPublisher(unittest.TestCase):

    @patch("app.services.alerts.AlertsService.get_user_device")
    @patch("app.firebase.firebase.FirebaseClient.send_fcm_alert")
    @patch("app.config.db.get_db")
    def test_send_alert(self, mock_get_db, mock_send_fcm_alert, mock_get_user_device):
        mock_db = MagicMock()
        mock_get_db.side_effect = [mock_db]

        fake_token = fake.uuid4()
        mock_get_user_device.return_value = fake_token
        mock_send_fcm_alert.return_value = None

        Publisher.send_alert("user_id", "priority", "title", "message")

        mock_get_user_device.assert_called_once_with("user_id")
        mock_send_fcm_alert.assert_called_once_with(fake_token, "priority", "title", "message")
