import json
import unittest

from unittest.mock import patch

from faker import Faker
from app.security.passwords import PasswordManager

fake = Faker()


def fake_encode_function(payload, secret, algorithm):
    return json.dumps({"payload": payload, "secret": secret, "algorithm": algorithm})


def fake_decode_function(token, secret, algorithm):
    return json.loads(token)


class TestPasswordManager(unittest.TestCase):
    @patch("bcrypt.hashpw")
    @patch("bcrypt.gensalt")
    def test_hash_password(self, mock_gensalt, mock_hashpw):
        fake_password = fake.word()
        fake_gen_salt = fake.word()
        fake_hashed_password = f"{fake_gen_salt} {fake_password}"
        mock_gensalt.return_value = fake_gen_salt
        mock_hashpw.return_value = fake_hashed_password.encode("utf-8")

        hashed_password = PasswordManager.get_password_hash(fake_password)
        self.assertEqual(hashed_password, fake_hashed_password)

    @patch("bcrypt.checkpw")
    def test_verify_password(self, mock_checkpw):
        fake_password = fake.word()
        fake_hashed_password = fake.word()
        mock_checkpw.return_value = True

        is_valid = PasswordManager.verify_password(fake_password, fake_hashed_password)
        self.assertTrue(is_valid)

    @patch("bcrypt.checkpw")
    def test_verify_password_invalid(self, mock_checkpw):
        fake_password = fake.word()
        fake_hashed_password = fake.word()
        mock_checkpw.return_value = False

        is_valid = PasswordManager.verify_password(fake_password, fake_hashed_password)
        self.assertFalse(is_valid)
