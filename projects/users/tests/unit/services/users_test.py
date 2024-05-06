import unittest

from unittest.mock import MagicMock, patch
from uuid import UUID

from faker import Faker
from sqlalchemy.orm import Session

from app.models.mappers.user_mapper import DataClassMapper
from app.models.schemas.profiles_schema import UserSportsProfileUpdate
from app.models.schemas.schema import CreateTrainingLimitation
from app.services.users import UsersService
from app.exceptions.exceptions import NotFoundError, InvalidCredentialsError, PlanPaymentError
from app.models.users import User, NutritionalLimitation, TrainingLimitation, UserSubscriptionType, PremiumAppointmentType

from tests.utils.users_util import (
    generate_random_user_create_data,
    generate_random_user_additional_information,
    generate_random_user_login_data,
    generate_random_user,
    generate_random_user_personal_profile,
    generate_random_user_sports_profile,
    generate_random_user_nutritional_profile,
    generate_random_update_user_plan,
    generate_random_trainer,
    generate_random_appointment_data,
    generate_random_appointment,
)

fake = Faker()


class TestUsersService(unittest.TestCase):
    def setUp(self):
        self.mock_jwt = MagicMock()
        self.mock_db = MagicMock(spec=Session)
        self.external_services = MagicMock()
        self.users_service = UsersService(db=self.mock_db)
        self.users_service.jwt_manager = self.mock_jwt
        self.users_service.external_services = self.external_services

    @patch("bcrypt.hashpw")
    @patch("bcrypt.gensalt")
    def test_create_users(self, mock_gensalt, mock_hashpw):
        user_1 = generate_random_user_create_data(fake)
        user_2 = generate_random_user_create_data(fake)
        user_3 = generate_random_user_create_data(fake)

        users_data = [user_1, user_2, user_3]

        users_created_fetch_all = [
            [user_1.first_name, user_1.last_name, user_1.email, "hashed" + user_1.password],
            [user_2.first_name, user_2.last_name, user_2.email, "hashed" + user_2.password],
            [user_3.first_name, user_3.last_name, user_3.email, "hashed" + user_3.password],
        ]

        execute_mock = MagicMock()
        self.mock_db.execute.return_value = execute_mock
        execute_mock.fetchall.return_value = users_created_fetch_all
        self.mock_db.commit.return_value = None
        self.users_service.create_users(users_data)
        mock_gensalt.return_value = b"somesalt"
        mock_hashpw.side_effect = lambda password, salt: b"hashed" + password

        self.assertEqual(mock_gensalt.call_count, 3)
        self.assertEqual(mock_hashpw.call_count, 3)
        self.assertEqual(self.mock_db.execute.call_count, 1)
        self.assertEqual(execute_mock.fetchall.call_count, 1)
        self.assertEqual(self.mock_db.commit.call_count, 1)

    @patch("app.models.mappers.user_mapper.DataClassMapper.to_dict")
    def test_complete_user_registration(self, mock_to_dict):
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

        mock_to_dict.to_dict.return_value = user.__dict__
        self.mock_db.commit.return_value = None

        self.users_service.complete_user_registration(user_id=user_id, user_additional_information=user_additional_info)

        mock_to_dict.assert_called_once_with(mock_first)
        self.assertEqual(self.mock_db.query.call_count, 1)
        self.assertEqual(self.mock_db.commit.call_count, 1)

    @patch("app.models.mappers.user_mapper.DataClassMapper.to_dict")
    def test_complete_user_registration_non_existing_user(self, mock_to_dict):
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

        mock_to_dict.to_dict.return_value = user.__dict__
        self.mock_db.commit.return_value = None

        with self.assertRaises(NotFoundError) as context:
            self.users_service.complete_user_registration(user_id, user_additional_info)
        self.assertEqual(str(context.exception), f"User with id {user_id} not found")

    @patch("app.security.passwords.PasswordManager.verify_password")
    def test_authenticate_user_email_password(self, mock_verify_password):
        user_credentials = generate_random_user_login_data(fake)

        mock_query = MagicMock()
        mock_filter = MagicMock()
        mocked_user = MagicMock()

        self.mock_db.query.return_value = mock_query
        mock_query.filter.return_value = mock_filter
        mock_filter.first.return_value = mocked_user
        mocked_user.hashed_password = f"hashed-{user_credentials.password}"

        mock_verify_password.return_value = True

        token_data = {
            "user_id": fake.uuid4(),
            "access_token": fake.sha256(),
            "access_token_expires_minutes": fake.random_int(min=1, max=60),
            "refresh_token": fake.sha256(),
            "refresh_token_expires_minutes": fake.random_int(min=1, max=60),
        }
        self.users_service.jwt_manager.generate_tokens.return_value = token_data

        response = self.users_service.authenticate_user(user_credentials)

        self.assertEqual(response, token_data)

    @patch("app.security.passwords.PasswordManager.verify_password")
    def test_authenticate_user_email_password_invalid_password(self, mock_verify_password):
        user_credentials = generate_random_user_login_data(fake)
        mock_query = MagicMock()
        mock_filter = MagicMock()
        mocked_user = MagicMock()

        self.mock_db.query.return_value = mock_query
        mock_query.filter.return_value = mock_filter
        mock_filter.first.return_value = mocked_user
        mock_verify_password.return_value = False

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
        user = generate_random_user(fake)
        user.user_id = fake.uuid4()

        token_data = {
            "user_id": fake.uuid4(),
            "access_token": fake.sha256(),
            "access_token_expires_minutes": fake.random_int(min=1, max=60),
            "refresh_token": fake.sha256(),
            "refresh_token_expires_minutes": fake.random_int(min=1, max=60),
        }
        self.users_service.jwt_manager.decode_refresh_token.return_value = user.user_id
        self.mock_db.query.return_value.filter.return_value.first.return_value = user
        self.users_service.jwt_manager.generate_tokens.return_value = token_data

        response = self.users_service.authenticate_user(user_credentials)

        self.assertEqual(response, token_data)

    def test_authenticate_user_refresh_token_invalid_token(self):
        user_credentials = generate_random_user_login_data(fake, token=True)

        self.users_service.jwt_manager.decode_refresh_token.side_effect = InvalidCredentialsError("Invalid or expired refresh token")

        with self.assertRaises(InvalidCredentialsError) as context:
            self.users_service.authenticate_user(user_credentials)
        self.assertEqual(str(context.exception), "Invalid or expired refresh token")

    @patch("app.models.mappers.user_mapper.DataClassMapper.to_user_personal_profile")
    def test_get_user_personal_profile(self, mock_to_user_personal_profile):
        user_id = fake.uuid4()
        user = generate_random_user(fake)
        user_personal_profile = generate_random_user_personal_profile(fake)
        self.mock_db.query.return_value.filter.return_value.first.return_value = user
        mock_to_user_personal_profile.return_value = user_personal_profile

        response = self.users_service.get_user_personal_information(user_id)

        self.assertEqual(response, user_personal_profile)
        mock_to_user_personal_profile.assert_called_once_with(user)
        self.mock_db.query.assert_called_once_with(User)
        self.mock_db.query.return_value.filter.assert_called_once()

    def test_get_user_personal_profile_user_not_found(self):
        user_id = fake.uuid4()
        self.mock_db.query.return_value.filter.return_value.first.return_value = None

        with self.assertRaises(NotFoundError) as context:
            self.users_service.get_user_personal_information(user_id)
        self.assertEqual(str(context.exception), f"User with id {user_id} not found")

    @patch("app.models.mappers.user_mapper.DataClassMapper.to_user_sports_profile")
    def test_get_user_sports_profile(self, mock_to_user_sports_profile):
        user_id = fake.uuid4()
        user = generate_random_user(fake)
        user_sports_profile = generate_random_user_sports_profile(fake)
        user_sports_profile_dict = DataClassMapper.to_dict(user_sports_profile, pydantic=True)
        self.mock_db.query.return_value.filter.return_value.first.return_value = user
        mock_to_user_sports_profile.return_value = user_sports_profile_dict

        response = self.users_service.get_user_sports_information(user_id)

        self.assertEqual(response, user_sports_profile_dict)
        mock_to_user_sports_profile.assert_called_once_with(user)
        self.mock_db.query.assert_called_once_with(User)
        self.mock_db.query.return_value.filter.assert_called_once()

    @patch("app.models.mappers.user_mapper.DataClassMapper.to_user_sports_profile")
    def test_get_user_sports_profile_no_bmi(self, mock_to_user_sports_profile):
        user_id = fake.uuid4()
        user = generate_random_user(fake)
        user_sports_profile = generate_random_user_sports_profile(fake)
        user_sports_profile.weight = None
        user_sports_profile.height = None
        user_sports_profile_dict = DataClassMapper.to_dict(user_sports_profile, pydantic=True)
        self.mock_db.query.return_value.filter.return_value.first.return_value = user
        mock_to_user_sports_profile.return_value = user_sports_profile_dict

        response = self.users_service.get_user_sports_information(user_id)

        self.assertEqual(response, user_sports_profile_dict)
        self.assertNotIn("bmi", response)
        mock_to_user_sports_profile.assert_called_once_with(user)
        self.mock_db.query.assert_called_once_with(User)
        self.mock_db.query.return_value.filter.assert_called_once()

    def test_get_user_sports_profile_user_not_found(self):
        user_id = fake.uuid4()
        self.mock_db.query.return_value.filter.return_value.first.return_value = None

        with self.assertRaises(NotFoundError) as context:
            self.users_service.get_user_sports_information(user_id)
        self.assertEqual(str(context.exception), f"User with id {user_id} not found")

    @patch("app.models.mappers.user_mapper.DataClassMapper.to_user_nutritional_profile")
    def test_get_user_nutritional_profile(self, mock_to_user_nutritional_profile):
        user_id = fake.uuid4()
        user = generate_random_user(fake)
        user.weight = None
        user.height = None
        user_nutritional_profile = generate_random_user_nutritional_profile(fake)

        user_nutritional_profile_dict = DataClassMapper.to_dict(user_nutritional_profile, pydantic=True)
        self.mock_db.query.return_value.filter.return_value.first.return_value = user
        mock_to_user_nutritional_profile.return_value = user_nutritional_profile_dict

        response = self.users_service.get_user_nutritional_information(user_id)

        self.assertEqual(response, user_nutritional_profile_dict)
        mock_to_user_nutritional_profile.assert_called_once_with(user)
        self.mock_db.query.assert_called_once_with(User)
        self.mock_db.query.return_value.filter.assert_called_once()

    def test_get_user_nutritional_profile_user_not_found(self):
        user_id = fake.uuid4()
        self.mock_db.query.return_value.filter.return_value.first.return_value = None

        with self.assertRaises(NotFoundError) as context:
            self.users_service.get_user_nutritional_information(user_id)
        self.assertEqual(str(context.exception), f"User with id {user_id} not found")

    @patch("app.models.mappers.user_mapper.DataClassMapper.to_dict")
    def test_get_nutritional_limitations(self, mock_to_dict):
        limitations = [
            {
                "limitation_id": str(fake.uuid4()),
                "limitation_name": fake.word(),
                "limitation_description": fake.sentence(),
            },
            {
                "limitation_id": str(fake.uuid4()),
                "limitation_name": fake.word(),
                "limitation_description": fake.sentence(),
            },
        ]

        self.mock_db.query.return_value.all.return_value = limitations
        mock_to_dict.side_effect = lambda limitation: limitation

        response = self.users_service.get_nutritional_limitations()

        self.assertEqual(response, limitations)
        self.assertEqual(mock_to_dict.call_count, 2)
        self.mock_db.query.assert_called_once_with(NutritionalLimitation)

    @patch("app.models.mappers.user_mapper.DataClassMapper.to_user_personal_profile")
    def test_update_user_personal_profile(self, mock_to_user_personal_profile):
        user_id = fake.uuid4()
        user = generate_random_user(fake)

        user_personal_profile_updated = generate_random_user_personal_profile(fake)
        user_personal_profile_updated_dict = DataClassMapper.to_dict(user_personal_profile_updated, pydantic=True)

        self.mock_db.query.return_value.filter.return_value.first.return_value = user
        mock_to_user_personal_profile.return_value = user_personal_profile_updated_dict

        response = self.users_service.update_user_personal_information(user_id, user_personal_profile_updated)

        self.assertEqual(response, user_personal_profile_updated_dict)
        mock_to_user_personal_profile.assert_called_once_with(user)
        self.mock_db.query.assert_called_once_with(User)
        self.mock_db.query.return_value.filter.assert_called_once()

    @patch("app.models.mappers.user_mapper.DataClassMapper.to_user_sports_profile")
    @patch("app.services.external.ExternalServices.get_sport")
    @patch("app.services.external.ExternalServices.create_training_plan")
    def test_update_user_sports_profile(self, mock_create_training_plan, mock_get_sport, mock_to_user_sports_profile):
        user_id = fake.uuid4()
        user = generate_random_user(fake)
        user_training_limitations = [
            TrainingLimitation(limitation_id=fake.uuid4(), name=fake.word(), description=fake.sentence()),
        ]

        updated_limitations = [
            CreateTrainingLimitation(name=fake.word(), description=fake.sentence()),
            CreateTrainingLimitation(name=fake.word(), description=fake.sentence()),
            CreateTrainingLimitation(limitation_id=user_training_limitations[0].limitation_id, name=fake.word(), description=fake.sentence()),
        ]

        user_sports_profile_updated = UserSportsProfileUpdate(
            height=fake.random_int(150, 200) / 100,
            weight=fake.random_int(40, 120),
            favourite_sport_id=fake.uuid4(),
            training_limitations=updated_limitations,
        )

        user_sports_profile_updated_dict = DataClassMapper.to_dict(user_sports_profile_updated, pydantic=True)

        self.mock_db.query.return_value.filter.return_value.first.side_effect = [user, user_training_limitations[0]]
        mock_to_user_sports_profile.return_value = user_sports_profile_updated_dict

        mock_get_sport.return_value = {"sport_id": user_sports_profile_updated.favourite_sport_id}

        mock_create_training_plan.return_value = None

        response = self.users_service.update_user_sports_information(user_id, user_sports_profile_updated)

        self.assertEqual(response, user_sports_profile_updated_dict)
        self.assertEqual(self.mock_db.query.call_count, 2)
        self.assertEqual(self.mock_db.query.return_value.filter.call_count, 2)

    @patch("app.models.mappers.user_mapper.DataClassMapper.to_user_sports_profile")
    def test_update_user_sports_profile_not_ready_to_create_training_plan(self, mock_to_user_sports_profile):
        user_id = fake.uuid4()
        user = generate_random_user(fake)
        user_training_limitations = [
            TrainingLimitation(limitation_id=fake.uuid4(), name=fake.word(), description=fake.sentence()),
        ]

        del user.training_objective

        updated_limitations = [
            CreateTrainingLimitation(name=fake.word(), description=fake.sentence()),
            CreateTrainingLimitation(name=fake.word(), description=fake.sentence()),
            CreateTrainingLimitation(limitation_id=user_training_limitations[0].limitation_id, name=fake.word(), description=fake.sentence()),
        ]

        user_sports_profile_updated = UserSportsProfileUpdate(
            height=fake.random_int(150, 200) / 100,
            weight=fake.random_int(40, 120),
            favourite_sport_id=fake.uuid4(),
            training_limitations=updated_limitations,
        )

        user_sports_profile_updated_dict = DataClassMapper.to_dict(user_sports_profile_updated, pydantic=True)

        self.mock_db.query.return_value.filter.return_value.first.side_effect = [user, user_training_limitations[0]]
        mock_to_user_sports_profile.return_value = user_sports_profile_updated_dict

        self.external_services.get_sport.return_value = {"sport_id": user_sports_profile_updated.favourite_sport_id}

        self.external_services.create_training_plan.return_value = None

        self.users_service.update_user_sports_information(user_id, user_sports_profile_updated)

        self.assertEqual(self.external_services.get_sport.call_count, 1)
        self.assertEqual(self.external_services.create_training_plan.call_count, 0)

    def test_update_user_sports_profile_invalid_sport(self):
        user_id = fake.uuid4()
        user = generate_random_user(fake)
        user_sports_profile_updated = UserSportsProfileUpdate(favourite_sport_id=UUID(fake.uuid4()))

        self.mock_db.query.return_value.filter.return_value.first.return_value = user
        self.external_services.get_sport.side_effect = NotFoundError(f"Sport with id {user_sports_profile_updated.favourite_sport_id} not found")

        with self.assertRaises(NotFoundError) as context:
            self.users_service.update_user_sports_information(user_id, user_sports_profile_updated)
        self.assertEqual(str(context.exception), f"Sport with id {user_sports_profile_updated.favourite_sport_id} not found")

    @patch("app.models.mappers.user_mapper.DataClassMapper.to_user_sports_profile")
    @patch("app.services.external.ExternalServices.get_sport")
    def test_update_user_sports_profile_invalid_training_limitation(self, mock_get_sport, mock_to_user_sports_profile):
        user_id = fake.uuid4()
        user = generate_random_user(fake)
        user_training_limitations = [
            TrainingLimitation(limitation_id=fake.uuid4(), name=fake.word(), description=fake.sentence()),
        ]

        updated_limitations = [
            CreateTrainingLimitation(name=fake.word(), description=fake.sentence()),
            CreateTrainingLimitation(name=fake.word(), description=fake.sentence()),
            CreateTrainingLimitation(limitation_id=user_training_limitations[0].limitation_id, name=fake.word(), description=fake.sentence()),
        ]

        user_sports_profile_updated = UserSportsProfileUpdate(
            training_limitations=updated_limitations,
        )

        user_sports_profile_updated_dict = DataClassMapper.to_dict(user_sports_profile_updated, pydantic=True)

        self.mock_db.query.return_value.filter.return_value.first.side_effect = [user, None]
        mock_to_user_sports_profile.return_value = user_sports_profile_updated_dict

        mock_get_sport.return_value = {"sport_id": user_sports_profile_updated.favourite_sport_id}

        with self.assertRaises(NotFoundError) as context:
            self.users_service.update_user_sports_information(user_id, user_sports_profile_updated)
        self.assertEqual(str(context.exception), f"Training limitation with id {user_training_limitations[0].limitation_id} not found")

    @patch("app.models.mappers.user_mapper.DataClassMapper.to_user_nutritional_profile")
    def test_update_user_nutritional_profile(self, mock_to_user_nutritional_profile):
        user_id = fake.uuid4()
        user = generate_random_user(fake)

        user_nutritional_profile_updated = generate_random_user_nutritional_profile(fake)
        user_nutritional_profile_updated_dict = DataClassMapper.to_dict(user_nutritional_profile_updated, pydantic=True)

        nutritional_limitation = NutritionalLimitation(
            limitation_id=fake.uuid4(),
            name=fake.word(),
            description=fake.sentence(),
        )

        nutritional_limitation_2 = NutritionalLimitation(
            limitation_id=fake.uuid4(),
            name=fake.word(),
            description=fake.sentence(),
        )
        self.mock_db.query.return_value.filter.return_value.first.side_effect = [user, nutritional_limitation, nutritional_limitation_2]
        mock_to_user_nutritional_profile.return_value = user_nutritional_profile_updated_dict

        response = self.users_service.update_user_nutritional_information(user_id, user_nutritional_profile_updated)

        self.assertEqual(response, user_nutritional_profile_updated_dict)
        mock_to_user_nutritional_profile.assert_called_once_with(user)
        self.assertEqual(self.mock_db.query.call_count, len(user.nutritional_limitations) + 1)
        self.assertEqual(self.mock_db.query.return_value.filter.call_count, len(user.nutritional_limitations) + 1)

    @patch("app.models.mappers.user_mapper.DataClassMapper.to_user_nutritional_profile")
    @patch("app.services.users.UsersService.get_user_by_id")
    def test_update_user_nutritional_profile_with_non_existing_limitations(self, mock_get_user_by_id, mock_to_user_nutritional_profile):
        user_id = fake.uuid4()
        user = generate_random_user(fake)

        user_nutritional_profile_updated = generate_random_user_nutritional_profile(fake)
        user_nutritional_profile_updated_dict = DataClassMapper.to_dict(user_nutritional_profile_updated, pydantic=True)

        mock_get_user_by_id.return_value = user
        self.mock_db.query.return_value.filter.return_value.first.return_value = None
        mock_to_user_nutritional_profile.return_value = user_nutritional_profile_updated_dict

        with self.assertRaises(NotFoundError) as context:
            self.users_service.update_user_nutritional_information(user_id, user_nutritional_profile_updated)
        self.assertEqual(str(context.exception), f"Nutritional limitation with id {user_nutritional_profile_updated.nutritional_limitations[0]} not found")

    @patch("app.services.users.UsersService.get_user_by_id")
    def test_update_user_plan_type(self, mock_get_user_by_id):
        user_id = fake.uuid4()
        user = generate_random_user(fake)
        user.plan_type = UserSubscriptionType.FREE

        mock_get_user_by_id.return_value = user

        self.external_services.process_payment.return_value = (True, {})

        update_user_plan_type = generate_random_update_user_plan(fake)
        update_user_plan_type.subscription_type = UserSubscriptionType.PREMIUM

        response = self.users_service.update_user_plan(user_id, update_user_plan_type)

        self.assertEqual(response["status"], "success")
        self.assertEqual(response["message"], "Subscription updated successfully")
        self.assertIn("subscription_start_date", response)
        self.assertIn("subscription_end_date", response)

    @patch("app.services.users.UsersService.get_user_by_id")
    def test_update_user_plan_type_free(self, mock_get_user_by_id):
        user_id = fake.uuid4()
        user = generate_random_user(fake)
        user.plan_type = UserSubscriptionType.PREMIUM

        mock_get_user_by_id.return_value = user

        update_user_plan_type = generate_random_update_user_plan(fake)
        update_user_plan_type.subscription_type = UserSubscriptionType.FREE

        response = self.users_service.update_user_plan(user_id, update_user_plan_type)

        self.assertEqual(response["status"], "success")
        self.assertEqual(response["message"], "Subscription updated successfully")
        self.assertNotIn("subscription_start_date", response)
        self.assertNotIn("subscription_end_date", response)

    @patch("app.services.users.UsersService.get_user_by_id")
    def test_update_user_plan_type_invalid_user(self, mock_get_user_by_id):
        user_id = fake.uuid4()

        mock_get_user_by_id.side_effect = NotFoundError(f"User with id {user_id} not found")

        with self.assertRaises(NotFoundError) as context:
            self.users_service.update_user_plan(user_id, generate_random_update_user_plan(fake))
        self.assertEqual(str(context.exception), f"User with id {user_id} not found")

    @patch("app.services.users.UsersService.get_user_by_id")
    def test_update_user_plan_type_payment_failed(self, mock_get_user_by_id):
        user_id = fake.uuid4()
        user = generate_random_user(fake)
        user.plan_type = UserSubscriptionType.FREE

        mock_get_user_by_id.return_value = user

        self.external_services.process_payment.return_value = (False, {"error": "Invalid card number"})

        update_user_plan_type = generate_random_update_user_plan(fake)
        update_user_plan_type.subscription_type = UserSubscriptionType.PREMIUM

        with self.assertRaises(PlanPaymentError) as context:
            self.users_service.update_user_plan(user_id, update_user_plan_type)
        self.assertEqual(str(context.exception), "Failed to process payment. Invalid card number")

    @patch("app.services.users.UsersService.get_user_by_id")
    def test_schedule_premium_sportsman_appointment_in_person(self, mock_get_user_by_id):
        user = generate_random_user(fake)
        trainer = generate_random_trainer(fake)

        appointment_data = generate_random_appointment_data(fake, trainer.trainer_id, address=True)
        appointment_data.appointment_type = PremiumAppointmentType.IN_PERSON

        mock_get_user_by_id.return_value = user

        self.mock_db.query.return_value.filter.return_value.first.return_value = trainer

        response = self.users_service.schedule_premium_sportsman_appointment(user_id=user.user_id, appointment_data=appointment_data)

        self.assertIn("appointment_date", response)
        self.assertEqual(response["appointment_type"], appointment_data.appointment_type.value)
        self.assertEqual(response["appointment_location"], appointment_data.appointment_location)
        self.assertEqual(response["trainer_id"], str(appointment_data.trainer_id))
        self.assertEqual(response["appointment_reason"], appointment_data.appointment_reason)

    @patch("app.services.users.UsersService.get_user_by_id")
    def test_schedule_premium_sportsman_appointment_virtual(self, mock_get_user_by_id):
        user = generate_random_user(fake)
        trainer = generate_random_trainer(fake)

        appointment_data = generate_random_appointment_data(fake, trainer.trainer_id)
        appointment_data.appointment_type = PremiumAppointmentType.VIRTUAL

        mock_get_user_by_id.return_value = user

        self.mock_db.query.return_value.filter.return_value.first.return_value = trainer

        response = self.users_service.schedule_premium_sportsman_appointment(user_id=user.user_id, appointment_data=appointment_data)

        self.assertIn("appointment_date", response)
        self.assertEqual(response["appointment_type"], appointment_data.appointment_type.value)
        self.assertNotIn("appointment_location", response)
        self.assertEqual(response["trainer_id"], str(appointment_data.trainer_id))
        self.assertEqual(response["appointment_reason"], appointment_data.appointment_reason)

    @patch("app.services.users.UsersService.get_user_by_id")
    def test_schedule_premium_sportsman_appointment_trainer_not_found(self, mock_get_user_by_id):
        user = generate_random_user(fake)
        appointment_data = generate_random_appointment_data(fake, fake.uuid4())

        mock_get_user_by_id.return_value = user
        self.mock_db.query.return_value.filter.return_value.first.return_value = None

        with self.assertRaises(NotFoundError) as context:
            self.users_service.schedule_premium_sportsman_appointment(user_id=user.user_id, appointment_data=appointment_data)
        self.assertEqual(str(context.exception), f"Trainer with id {appointment_data.trainer_id} not found")

    @patch("app.services.users.UsersService.get_user_by_id")
    def test_get_scheduled_appointments(self, mock_get_user_by_id):
        user = generate_random_user(fake)
        appointment_1 = generate_random_appointment(fake)
        appointment_2 = generate_random_appointment(fake)

        mock_get_user_by_id.return_value = user
        self.mock_db.query.return_value.filter.return_value.order_by.return_value.all.return_value = [appointment_1, appointment_2]

        response = self.users_service.get_scheduled_appointments(user_id=user.user_id)

        self.assertEqual(len(response), 2)
        for appointment in response:
            self.assertIn("appointment_date", appointment)
            self.assertIn("appointment_type", appointment)
            self.assertIn("appointment_location", appointment)
            self.assertIn("trainer_id", appointment)
            self.assertIn("appointment_reason", appointment)

    @patch("app.services.users.UsersService.get_user_by_id")
    def test_get_scheduled_appointments_user_not_found(self, mock_get_user_by_id):
        user_id = fake.uuid4()

        mock_get_user_by_id.side_effect = NotFoundError(f"User with id {user_id} not found")

        with self.assertRaises(NotFoundError) as context:
            self.users_service.get_scheduled_appointments(user_id)
        self.assertEqual(str(context.exception), f"User with id {user_id} not found")

    def test_get_premium_trainers(self):
        trainers = [generate_random_trainer(fake) for _ in range(3)]

        self.mock_db.query.return_value.all.return_value = trainers

        response = self.users_service.get_premium_trainers()

        self.assertEqual(len(response), 3)
        for trainer in response:
            self.assertIn("trainer_id", trainer)
            self.assertIn("first_name", trainer)
            self.assertIn("last_name", trainer)
