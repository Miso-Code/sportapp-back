import unittest

from unittest.mock import MagicMock, patch

from faker import Faker
from jose import JWTError
from sqlalchemy.orm import Session

from app.models.schemas.schema import UserCredentials
from app.services.users import UsersService
from app.exceptions.exceptions import NotFoundError, InvalidCredentialsError
from app.models.users import User
from app.models.mappers.mapper import DataClassMapper

from tests.utils.users_util import generate_random_user_create_data, generate_random_user_additional_information, generate_random_user_login_data

fake = Faker()


class TestUsersService(unittest.TestCase):
    def setUp(self):
        self.mock_jwt = MagicMock()
        self.mock_mapper = MagicMock(spec=DataClassMapper)
        self.mock_db = MagicMock(spec=Session)
        self.users_service = UsersService(db=self.mock_db)
        self.users_service.mapper = self.mock_mapper
        self.users_service.jwt_manager = self.mock_jwt

    @patch("bcrypt.hashpw")
    @patch("bcrypt.gensalt")
    def test_create_users(self, mock_gensalt, mock_hashpw):
        user_1 = generate_random_user_create_data(fake)
        user_2 = generate_random_user_create_data(fake)
        user_3 = generate_random_user_create_data(fake)

        users_data = [user_1, user_2, user_3]

        users_data_dict = [user_1.dict(), user_2.dict(), user_3.dict()]
        self.mock_mapper.to_dict.side_effect = users_data_dict
        self.mock_db.bulk_save_objects.return_value = None
        self.mock_db.commit.return_value = None
        self.users_service.create_users(users_data)
        mock_gensalt.return_value = b"somesalt"
        mock_hashpw.side_effect = lambda password, salt: b"hashed" + password

        self.assertEqual(mock_gensalt.call_count, 3)
        self.assertEqual(mock_hashpw.call_count, 3)
        self.assertEqual(self.mock_db.bulk_save_objects.call_count, 1)
        self.assertEqual(self.mock_db.commit.call_count, 1)

    def test_complete_user_registration(self):
        user_create_data = generate_random_user_create_data(fake)
        user_additional_info = generate_random_user_additional_information(fake)
        user_id = fake.uuid4()

        user = User(
            user_id=user_id,
            first_name=user_create_data.first_name,
            last_name=user_create_data.last_name,
            email=user_create_data.email,
            hashed_password=f"hashed-{user_create_data.password}",
        )

        mock_query = MagicMock()
        mock_filter = MagicMock()
        mock_first = MagicMock(return_value=user)

        self.mock_db.query.return_value = mock_query
        mock_query.filter.return_value = mock_filter
        mock_filter.first.return_value = mock_first

        self.mock_mapper.to_dict.return_value = user.__dict__
        self.mock_db.commit.return_value = None

        self.users_service.complete_user_registration(user_id=user_id, user_additional_information=user_additional_info)

        self.assertEqual(self.mock_mapper.to_dict.call_count, 1)
        self.assertEqual(self.mock_db.query.call_count, 1)
        self.assertEqual(self.mock_db.commit.call_count, 1)

    def test_complete_user_registration_non_existing_user(self):
        user_create_data = generate_random_user_create_data(fake)
        user_additional_info = generate_random_user_additional_information(fake)
        user_id = fake.uuid4()

        user = User(
            user_id=user_id,
            first_name=user_create_data.first_name,
            last_name=user_create_data.last_name,
            email=user_create_data.email,
            hashed_password=f"hashed-{user_create_data.password}",
        )

        mock_query = MagicMock()
        mock_filter = MagicMock()

        self.mock_db.query.return_value = mock_query
        mock_query.filter.return_value = mock_filter
        mock_filter.first.return_value = None

        self.mock_mapper.to_dict.return_value = user.__dict__
        self.mock_db.commit.return_value = None

        with self.assertRaises(NotFoundError) as context:
            self.users_service.complete_user_registration(user_id, user_additional_info)
        self.assertEqual(str(context.exception), f"User with id {user_id} not found")

    @patch("bcrypt.checkpw")
    def test_authenticate_user_email_password(self, mock_checkpw):
        user_credentials = generate_random_user_login_data(fake)

        mock_query = MagicMock()
        mock_filter = MagicMock()
        mocked_user = MagicMock()

        self.mock_db.query.return_value = mock_query
        mock_query.filter.return_value = mock_filter
        mock_filter.first.return_value = mocked_user
        mocked_user.hashed_password = f"hashed-{user_credentials.password}"

        mock_checkpw.return_value = True

        token_data = {
            "access_token": fake.sha256(),
            "access_token_expires_minutes": fake.random_int(min=1, max=60),
            "refresh_token": fake.sha256(),
            "refresh_token_expires_minutes": fake.random_int(min=1, max=60),
        }
        self.users_service.jwt_manager.generate_tokens.return_value = token_data

        response = self.users_service.authenticate_user(user_credentials)

        self.assertEqual(response, token_data)

    @patch("bcrypt.checkpw")
    def test_authenticate_user_email_password_invalid_password(self, mock_checkpw):
        user_credentials = generate_random_user_login_data(fake)
        mock_query = MagicMock()
        mock_filter = MagicMock()
        mocked_user = MagicMock()

        self.mock_db.query.return_value = mock_query
        mock_query.filter.return_value = mock_filter
        mock_filter.first.return_value = mocked_user
        mocked_user.hashed_password = f"hashed-{user_credentials.password}"

        mock_checkpw.return_value = False

        with self.assertRaises(InvalidCredentialsError) as context:
            self.users_service.authenticate_user(user_credentials)
        self.assertEqual(str(context.exception), "Invalid email or password")

    def test_authenticate_user_email_password_user_not_found(self):
        user_credentials = generate_random_user_login_data(fake)
        mock_query = MagicMock()
        mock_filter = MagicMock()
        self.mock_db.query.return_value = mock_query
        mock_query.filter.return_value = mock_filter
        mock_filter.first.return_value = None

        with self.assertRaises(InvalidCredentialsError) as context:
            self.users_service.authenticate_user(user_credentials)
        self.assertEqual(str(context.exception), "Invalid email or password")

    def test_authenticate_user_refresh_token(self):
        user_credentials = generate_random_user_login_data(fake, token=True)

        token_data = {
            "access_token": fake.sha256(),
            "access_token_expires_minutes": fake.random_int(min=1, max=60),
            "refresh_token": fake.sha256(),
            "refresh_token_expires_minutes": fake.random_int(min=1, max=60),
        }
        self.users_service.jwt_manager.refresh_token.return_value = token_data

        response = self.users_service.authenticate_user(user_credentials)

        self.assertEqual(response, token_data)

    def test_authenticate_user_refresh_token_invalid_token(self):
        user_credentials = generate_random_user_login_data(fake, token=True)

        self.users_service.jwt_manager.refresh_token.side_effect = JWTError("Invalid token")

        with self.assertRaises(InvalidCredentialsError) as context:
            self.users_service.authenticate_user(user_credentials)
        self.assertEqual(str(context.exception), "Invalid or expired refresh token")
