from unittest.mock import patch

import faker

from app.utils import utils

fake = faker.Faker()


class TestUtils:

    def test_validate_api_key(self):
        fake_api_key = fake.word()
        with patch("app.utils.utils.Config.SPORT_SESSIONS_API_KEY", fake_api_key):
            response = utils.validate_api_key(fake_api_key)
            assert response == fake_api_key

    def test_validate_api_key_invalid(self):
        fake_api_key = fake.word()
        with patch("app.utils.utils.Config.SPORT_SESSIONS_API_KEY", fake.word()):
            try:
                utils.validate_api_key(fake_api_key)
            except Exception as e:
                assert str(e) == "Invalid API key"

    def test_validate_api_key_none(self):
        with patch("app.utils.utils.Config.SPORT_SESSIONS_API_KEY", fake.word()):
            try:
                utils.validate_api_key(None)
            except Exception as e:
                assert str(e) == "Invalid API key"
