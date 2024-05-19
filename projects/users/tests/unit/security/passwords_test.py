import json
import unittest

from unittest.mock import patch, MagicMock

from faker import Faker
from app.security.passwords import PasswordManager

fake = Faker()


def fake_encode_function(payload, secret, algorithm):
    return json.dumps({"payload": payload, "secret": secret, "algorithm": algorithm})


def fake_decode_function(token, _, _2):
    return json.loads(token)


class TestPasswordManager(unittest.TestCase):
    @patch("hashlib.sha256")
    def test_hash_password(self, mock_sha256):
        fake_password = fake.word()
        fake_hashed_password = f"hashed-{fake_password}"
        sha256_mock = MagicMock()
        mock_sha256.return_value = sha256_mock
        sha256_mock.update.return_value = None
        sha256_mock.hexdigest.return_value = fake_hashed_password

        hashed_password = PasswordManager.get_password_hash(fake_password)
        self.assertEqual(hashed_password, fake_hashed_password)

    @patch("hashlib.sha256")
    def test_verify_password(self, mock_sha256):
        fake_password = fake.word()
        fake_hashed_password = f"hashed-{fake_password}"
        sha256_mock = MagicMock()
        mock_sha256.return_value = sha256_mock
        sha256_mock.update.return_value = None
        sha256_mock.hexdigest.return_value = fake_hashed_password

        is_valid = PasswordManager.verify_password(fake_password, fake_hashed_password)
        self.assertTrue(is_valid)

    @patch("bcrypt.checkpw")
    def test_verify_password_invalid(self, mock_checkpw):
        fake_password = fake.word()
        fake_hashed_password = fake.word()
        mock_checkpw.return_value = False

        is_valid = PasswordManager.verify_password(fake_password, fake_hashed_password)
        self.assertFalse(is_valid)
