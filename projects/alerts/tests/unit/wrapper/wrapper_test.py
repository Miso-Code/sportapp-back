import unittest
from unittest.mock import patch

from app.wrapper.firebase_wrapper import FirebaseWrapper


class WrapperTest(unittest.TestCase):
    def test_wrapper(self):
        firebase_wrapper = FirebaseWrapper()

        self.assertIsNotNone(firebase_wrapper.messaging)
        self.assertIsNotNone(firebase_wrapper.credentials)
        self.assertIsNotNone(firebase_wrapper.initialize_app)

    @patch("firebase_admin.credentials.Certificate")
    @patch("json.loads")
    def test_generate_credentials(self, mock_certificate, mock_json):
        firebase_wrapper = FirebaseWrapper()
        mock_json.return_value = {"key": "value"}
        response = firebase_wrapper.generate_credentials()

        self.assertEqual(response, {"key": "value"})
