import unittest

from unittest.mock import MagicMock, patch

from faker import Faker
from sqlalchemy.orm import Session

from app.services.business_partners import BusinessPartnersService
from app.exceptions.exceptions import InvalidCredentialsError, EntityExistsError

from tests.utils.users_util import (
    generate_random_user_create_data,
    generate_random_user_login_data,
    generate_random_user,
    generate_random_business_partner_create_data,
)

fake = Faker()


class TestBusinessPartnersService(unittest.TestCase):
    def setUp(self):
        self.mock_jwt = MagicMock()
        self.mock_db = MagicMock(spec=Session)
        self.business_partners_service = BusinessPartnersService(db=self.mock_db)
        self.business_partners_service.jwt_manager = self.mock_jwt

    @patch("app.security.passwords.PasswordManager.get_password_hash")
    @patch("app.models.mappers.user_mapper.DataClassMapper.to_dict")
    def test_create_business_partner(self, to_dict_mock, get_password_hash_mock):
        business_partner_create = generate_random_business_partner_create_data(fake)
        business_partner_created = {
            "business_partner_id": fake.uuid4(),
            "email": business_partner_create.email,
            "business_partner_name": business_partner_create.business_partner_name,
        }

        mock_query = MagicMock()
        mock_filter = MagicMock()

        self.mock_db.query.return_value = mock_query
        mock_query.filter.return_value = mock_filter
        mock_filter.first.return_value = None

        to_dict_mock.return_value = business_partner_created

        get_password_hash_mock.return_value = f"hashed-{business_partner_create.password}".encode()

        response = self.business_partners_service.create_business_partner(business_partner_create)

        self.assertEqual(response["email"], business_partner_create.email)
        self.assertEqual(response["business_partner_name"], business_partner_create.business_partner_name)
        self.assertIn("business_partner_id", response)

    def test_create_business_partner_already_exists(self):
        business_partner_data = generate_random_user_create_data(fake)

        mock_query = MagicMock()
        mock_filter = MagicMock()

        self.mock_db.query.return_value = mock_query
        mock_query.filter.return_value = mock_filter
        mock_filter.first.return_value = generate_random_user(fake)

        with self.assertRaises(EntityExistsError) as context:
            self.business_partners_service.create_business_partner(business_partner_data)
        self.assertEqual(str(context.exception), "Business partner with this email already exists")

    def test_authenticate_user_email_password(self):
        business_partner_credentials = generate_random_user_login_data(fake)

        mock_query = MagicMock()
        mock_filter = MagicMock()
        mocked_business_partner = MagicMock()

        self.mock_db.query.return_value = mock_query
        mock_query.filter.return_value = mock_filter
        mock_filter.first.return_value = mocked_business_partner
        mocked_business_partner.hashed_password = f"hashed-{business_partner_credentials.password}"

        token_data = {
            "user_id": fake.uuid4(),
            "access_token": fake.sha256(),
            "access_token_expires_minutes": fake.random_int(min=1, max=60),
            "refresh_token": fake.sha256(),
            "refresh_token_expires_minutes": fake.random_int(min=1, max=60),
        }
        self.business_partners_service.jwt_manager.process_email_password_login.return_value = token_data

        response = self.business_partners_service.authenticate_business_partner(business_partner_credentials)

        self.assertEqual(response, token_data)

    def test_authenticate_user_email_password_invalid_password(self):
        user_credentials = generate_random_user_login_data(fake)
        mock_query = MagicMock()
        mock_filter = MagicMock()
        mocked_business_partner = MagicMock()

        self.mock_db.query.return_value = mock_query
        mock_query.filter.return_value = mock_filter
        mock_filter.first.return_value = mocked_business_partner
        mocked_business_partner.hashed_password = f"hashed-{user_credentials.password}"

        self.business_partners_service.jwt_manager.process_email_password_login.side_effect = InvalidCredentialsError("Invalid email or password")

        with self.assertRaises(InvalidCredentialsError) as context:
            self.business_partners_service.authenticate_business_partner(user_credentials)
        self.assertEqual(str(context.exception), "Invalid email or password")

    def test_authenticate_user_email_password_user_not_found(self):
        user_credentials = generate_random_user_login_data(fake)
        mock_query = MagicMock()
        mock_filter = MagicMock()
        self.mock_db.query.return_value = mock_query
        mock_query.filter.return_value = mock_filter
        mock_filter.first.return_value = None

        with self.assertRaises(InvalidCredentialsError) as context:
            self.business_partners_service.authenticate_business_partner(user_credentials)
        self.assertEqual(str(context.exception), "Invalid email or password")

    def test_authenticate_user_refresh_token(self):
        user_credentials = generate_random_user_login_data(fake, token=True)

        token_data = {
            "user_id": fake.uuid4(),
            "access_token": fake.sha256(),
            "access_token_expires_minutes": fake.random_int(min=1, max=60),
            "refresh_token": fake.sha256(),
            "refresh_token_expires_minutes": fake.random_int(min=1, max=60),
        }
        self.business_partners_service.jwt_manager.process_refresh_token_login.return_value = token_data

        response = self.business_partners_service.authenticate_business_partner(user_credentials)

        self.assertEqual(response, token_data)

    def test_authenticate_user_refresh_token_invalid_token(self):
        user_credentials = generate_random_user_login_data(fake, token=True)

        self.business_partners_service.jwt_manager.process_refresh_token_login.side_effect = InvalidCredentialsError("Invalid or expired refresh token")

        with self.assertRaises(InvalidCredentialsError) as context:
            self.business_partners_service.authenticate_business_partner(user_credentials)
        self.assertEqual(str(context.exception), "Invalid or expired refresh token")
