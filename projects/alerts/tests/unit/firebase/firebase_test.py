import unittest
from unittest.mock import patch

from app.firebase.firebase import FirebaseClient


class TestFirebase(unittest.TestCase):

    @patch("firebase_admin.messaging.send")
    def test_send_fcm_alert(self, mock_messaging_send):
        device_registration_token = "test_device_registration_token"
        priority = "test_priority"
        title = "test_title"
        message_data = "test_message_data"

        mock_messaging_send.side_effect = None

        FirebaseClient.send_fcm_alert(device_registration_token, priority, title, message_data)

        mock_messaging_send.assert_called_once()

    @patch("firebase_admin.messaging.send")
    def test_send_fcm_alert_no_device_registration_token(self, mock_messaging_send):
        device_registration_token = None
        priority = "test_priority"
        title = "test_title"
        message_data = "test_message_data"

        FirebaseClient.send_fcm_alert(device_registration_token, priority, title, message_data)

        mock_messaging_send.assert_not_called()
