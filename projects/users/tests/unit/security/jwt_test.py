import json
import unittest

from unittest.mock import patch

from datetime import datetime, timezone, timedelta
from faker import Faker
from jose import JWTError

from app.exceptions.exceptions import InvalidCredentialsError
from app.security.jwt import JWTManager

fake = Faker()


def fake_encode_function(payload, secret, algorithm):
    return json.dumps({"payload": payload, "secret": secret, "algorithm": algorithm})


def fake_decode_function(token, _, _2):
    return json.loads(token)


INVALID_EXPIRED_MESSAGE = "Invalid or expired refresh token"


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
        user_id = fake.uuid4()
        scopes = [fake.word() for _ in range(3)]
        mock_encode.side_effect = fake_encode_function

        response = self.jwt_manager.generate_tokens(user_id=user_id, scopes=scopes)
        self.assertIn("access_token", response)
        self.assertIn("access_token_expires_minutes", response)
        self.assertIn("refresh_token", response)
        self.assertIn("refresh_token_expires_minutes", response)

        self.assertEqual(response["access_token_expires_minutes"], self._access_token_expiry)
        self.assertEqual(response["refresh_token_expires_minutes"], self._refresh_token_expiry)

        self.assertIn(json.loads(response["access_token"])["payload"]["user_id"], user_id)

    @patch("jose.jwt.encode")
    @patch("jose.jwt.decode")
    def test_refresh_token(self, mock_decode, mock_encode):
        expiry = datetime.now(timezone.utc) + timedelta(minutes=10)
        user_id = fake.uuid4()
        scopes = [fake.word() for _ in range(3)]
        fake_decoded_token = {"user_id": user_id, "expiry": expiry.timestamp(), "scopes": scopes}
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
        self.assertEqual(str(context.exception), INVALID_EXPIRED_MESSAGE)

    @patch("jose.jwt.decode")
    def test_refresh_token_invalid(self, mock_decode):
        fake_token = fake.word()
        mock_decode.side_effect = JWTError("Invalid token")

        with self.assertRaises(InvalidCredentialsError) as context:
            self.jwt_manager.refresh_token(token=fake_token)
        self.assertEqual(str(context.exception), INVALID_EXPIRED_MESSAGE)

    @patch("jose.jwt.decode")
    def test_refresh_token_no_expiry(self, mock_decode):
        fake_decoded_token = {"username": fake.word()}
        fake_token = json.dumps(fake_decoded_token)
        mock_decode.side_effect = fake_decode_function

        with self.assertRaises(InvalidCredentialsError) as context:
            self.jwt_manager.refresh_token(token=fake_token)
        self.assertEqual(str(context.exception), INVALID_EXPIRED_MESSAGE)
