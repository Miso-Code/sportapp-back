import json
import unittest

from unittest.mock import MagicMock, patch

from datetime import datetime, timezone, timedelta
from faker import Faker
from jose import JWTError

from app.exceptions.exceptions import InvalidCredentialsError
from app.security.jwt import JWTManager

fake = Faker()


def fake_encode_function(payload, secret, algorithm):
    return json.dumps({"payload": payload, "secret": secret, "algorithm": algorithm})


def fake_decode_function(token, secret, algorithm):
    return json.loads(token)


class TestJWTManager(unittest.TestCase):
    def setUp(self):
        self._secret = fake.word()
        self._algorithm = fake.word()
        self._access_token_expiry = fake.random_int(1, 10)
        self._refresh_token_expiry = fake.random_int(1, 10)
        self.jwt_manager = JWTManager(
            secret_key=self._secret,
            algorithm=self._algorithm,
            access_token_expiry_minutes=self._access_token_expiry,
            refresh_token_expiry_minutes=self._refresh_token_expiry,
        )

    @patch("jose.jwt.encode")
    def test_generate_token(self, mock_encode):
        payload = {"username": fake.word()}
        mock_encode.side_effect = fake_encode_function

        response = self.jwt_manager.generate_tokens(payload=payload)
        self.assertIn("access_token", response)
        self.assertIn("access_token_expires_minutes", response)
        self.assertIn("refresh_token", response)
        self.assertIn("refresh_token_expires_minutes", response)

        self.assertEqual(response["access_token_expires_minutes"], self._access_token_expiry)
        self.assertEqual(response["refresh_token_expires_minutes"], self._refresh_token_expiry)

        self.assertIn(json.loads(response["access_token"])["payload"]["username"], payload["username"])

    @patch("jose.jwt.encode")
    @patch("jose.jwt.decode")
    def test_refresh_token(self, mock_decode, mock_encode):
        expiry = datetime.now(timezone.utc) + timedelta(minutes=10)
        fake_decoded_token = {"username": fake.word(), "expiry": expiry.timestamp()}
        fake_token = json.dumps(fake_decoded_token)
        mock_encode.side_effect = fake_encode_function
        mock_decode.side_effect = fake_decode_function

        response = self.jwt_manager.refresh_token(token=fake_token)

        self.assertIn("access_token", response)
        self.assertIn("access_token_expires_minutes", response)
        self.assertIn("refresh_token", response)
        self.assertIn("refresh_token_expires_minutes", response)

    @patch("jose.jwt.encode")
    @patch("jose.jwt.decode")
    def test_refresh_token_expired(self, mock_decode, mock_encode):
        expiry = datetime.now(timezone.utc) - timedelta(minutes=1)
        fake_decoded_token = {"username": fake.word(), "expiry": expiry.timestamp()}
        fake_token = json.dumps(fake_decoded_token)
        mock_encode.side_effect = fake_encode_function
        mock_decode.side_effect = fake_decode_function

        with self.assertRaises(InvalidCredentialsError) as context:
            self.jwt_manager.refresh_token(token=fake_token)
        self.assertEqual(str(context.exception), "Invalid or expired refresh token")

    @patch("jose.jwt.decode")
    def test_refresh_token_invalid(self, mock_decode):
        fake_token = fake.word()
        mock_decode.side_effect = JWTError("Invalid token")

        with self.assertRaises(InvalidCredentialsError) as context:
            self.jwt_manager.refresh_token(token=fake_token)
        self.assertEqual(str(context.exception), "Invalid or expired refresh token")

    @patch("jose.jwt.decode")
    def test_refresh_token_no_expiry(self, mock_decode):
        fake_decoded_token = {"username": fake.word()}
        fake_token = json.dumps(fake_decoded_token)
        mock_decode.side_effect = fake_decode_function

        with self.assertRaises(InvalidCredentialsError) as context:
            self.jwt_manager.refresh_token(token=fake_token)
        self.assertEqual(str(context.exception), "Invalid or expired refresh token")
