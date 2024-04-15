import json
import unittest

from unittest.mock import patch, MagicMock

from faker import Faker

from app.models.schemas.schema import UserAdditionalInformation, UserCreate, UserCredentials
from app.routes import users_routes
from app.utils.user_cache import UserCache
from app.models.users import UserIdentificationType, Gender, TrainingObjective, TrainingFrequency, FoodPreference
from tests.utils.users_util import generate_random_user_personal_profile, generate_random_user_nutritional_profile, generate_random_user_sports_profile

fake = Faker()


class TestUsersRoutes(unittest.IsolatedAsyncioTestCase):
    async def asyncSetUp(self):
        UserCache.users = []
        UserCache.users_with_errors_by_email_map = {}
        UserCache.users_success_by_email_map = {}

    async def test_register_user(self):
        first_name = fake.first_name()
        last_name = fake.last_name()
        email = fake.email()
        password = f"{fake.password()}A123!"

        user_data = {"first_name": first_name, "last_name": last_name, "email": email, "password": password}

        user_create = UserCreate(**user_data)

        user_data["user_id"] = fake.uuid4()
        UserCache.users_success_by_email_map = {email: user_data}
        response = await users_routes.register_user(user_create)
        async_gen = response.body_iterator

        async for data in async_gen:
            json_data = json.loads(data.strip())
            self.assertEqual(json_data["status"], "success")
            self.assertEqual(json_data["message"], "User created")
            self.assertEqual(json_data["data"]["id"], user_data["user_id"])
            self.assertEqual(json_data["data"]["email"], email)
            self.assertEqual(json_data["data"]["first_name"], first_name)
            self.assertEqual(json_data["data"]["last_name"], last_name)
            break

        self.assertEqual(len(UserCache.users), 1)
        self.assertEqual(UserCache.users[0].first_name, first_name)
        self.assertEqual(UserCache.users[0].last_name, last_name)
        self.assertEqual(UserCache.users[0].email, email)
        self.assertEqual(UserCache.users[0].password, password)
        self.assertEqual(len(UserCache.users_success_by_email_map), 0)

    async def test_register_user_email_repeated(self):
        first_name = fake.first_name()
        last_name = fake.last_name()
        email = fake.email()
        password = f"{fake.password()}A123!"

        user_data = {"first_name": first_name, "last_name": last_name, "email": email, "password": password}

        user_create = UserCreate(**user_data)

        UserCache.users_with_errors_by_email_map = {email: user_data}
        response = await users_routes.register_user(user_create)
        async_gen = response.body_iterator

        error_response = {"status": "error", "message": "User already exists"}

        async for data in async_gen:
            json_data = json.loads(data.strip())
            self.assertEqual(json_data["status"], error_response["status"])
            self.assertEqual(json_data["message"], error_response["message"])
            break

        self.assertEqual(len(UserCache.users), 1)
        self.assertEqual(UserCache.users[0].first_name, first_name)
        self.assertEqual(UserCache.users[0].last_name, last_name)
        self.assertEqual(UserCache.users[0].email, email)
        self.assertEqual(UserCache.users[0].password, password)
        self.assertEqual(len(UserCache.users_with_errors_by_email_map), 0)

    async def test_register_user_processing(self):
        first_name = fake.first_name()
        last_name = fake.last_name()
        email = fake.email()
        password = f"{fake.password()}A123!"

        user_data = {"first_name": first_name, "last_name": last_name, "email": email, "password": password}

        user_create = UserCreate(**user_data)

        response = await users_routes.register_user(user_create)
        async_gen = response.body_iterator
        max_loops = 3

        processing_response = {"status": "processing", "message": "Processing..."}

        async for data in async_gen:
            json_data = json.loads(data.strip())
            self.assertEqual(json_data["status"], processing_response["status"])
            self.assertEqual(json_data["message"], processing_response["message"])
            max_loops -= 1
            if max_loops == 0:
                break
        self.assertEqual(UserCache.users[0].first_name, first_name)
        self.assertEqual(UserCache.users[0].last_name, last_name)
        self.assertEqual(UserCache.users[0].email, email)
        self.assertEqual(UserCache.users[0].password, password)
        self.assertEqual(len(UserCache.users_success_by_email_map), 0)
        self.assertEqual(len(UserCache.users_with_errors_by_email_map), 0)

    @patch("app.services.users.UsersService.complete_user_registration")
    async def test_complete_user_registration(self, complete_user_registration):
        user_id = fake.uuid4()
        identification_type = fake.enum(UserIdentificationType).value
        identification_number = fake.numerify(text="############")
        gender = fake.enum(Gender).value
        country_of_birth = fake.country()
        city_of_birth = fake.city()
        country_of_residence = fake.country()
        city_of_residence = fake.city()
        residence_age = fake.random_int(min=1, max=100)
        birth_date = fake.date_of_birth(minimum_age=18).strftime("%Y-%m-%d")

        user_data = {
            "identification_type": identification_type,
            "identification_number": identification_number,
            "gender": gender,
            "country_of_birth": country_of_birth,
            "city_of_birth": city_of_birth,
            "country_of_residence": country_of_residence,
            "city_of_residence": city_of_residence,
            "residence_age": residence_age,
            "birth_date": birth_date,
        }

        user_additional_information = UserAdditionalInformation(**user_data)

        db = MagicMock()
        complete_user_registration.return_value = user_data
        response = await users_routes.complete_user_registration(user_id, user_additional_information, db)
        response_body = json.loads(response.body)

        self.assertEqual(response.status_code, 200)
        self.assertEqual(response_body, user_data)

    @patch("app.services.users.UsersService.authenticate_user")
    async def test_login_user_email_password(self, authenticate_user_mock):
        email = fake.email()
        password = f"{fake.password()}A123!"

        user_data = {"email": email, "password": password}
        user_credentials = UserCredentials(**user_data)

        db = MagicMock()

        token_data = {
            "access_token": fake.sha256(),
            "access_token_expires_minutes": fake.random_int(min=1, max=60),
            "refresh_token": fake.sha256(),
            "refresh_token_expires_minutes": fake.random_int(min=1, max=60),
        }
        authenticate_user_mock.return_value = token_data

        response = await users_routes.login_user(user_credentials, db)
        response_body = json.loads(response.body)

        self.assertEqual(response.status_code, 200)
        authenticate_user_mock.assert_called_once_with(user_credentials)
        self.assertEqual(response_body, token_data)

    @patch("app.services.users.UsersService.authenticate_user")
    async def test_login_user_refresh_token(self, authenticate_user_mock):
        token = fake.sha256()
        user_data = {"refresh_token": token}
        user_credentials = UserCredentials(**user_data)

        db = MagicMock()

        token_data = {
            "access_token": fake.sha256(),
            "access_token_expires_minutes": fake.random_int(min=1, max=60),
            "refresh_token": fake.sha256(),
            "refresh_token_expires_minutes": fake.random_int(min=1, max=60),
        }
        authenticate_user_mock.return_value = token_data

        response = await users_routes.login_user(user_credentials, db)
        response_body = json.loads(response.body)

        self.assertEqual(response.status_code, 200)
        authenticate_user_mock.assert_called_once_with(user_credentials)
        self.assertEqual(response_body, token_data)

    @patch("app.services.users.UsersService.get_user_personal_information")
    async def test_get_user_personal_information(self, get_user_personal_information_mock):
        user_id = fake.uuid4()
        user_data = {
            "email": fake.email(),
            "first_name": fake.first_name(),
            "last_name": fake.last_name(),
            "identification_type": fake.enum(UserIdentificationType).value,
            "identification_number": fake.numerify(text="############"),
            "gender": fake.enum(Gender).value,
            "country_of_birth": fake.country(),
            "city_of_birth": fake.city(),
            "country_of_residence": fake.country(),
            "city_of_residence": fake.city(),
            "residence_age": fake.random_int(min=1, max=100),
            "birth_date": fake.date_of_birth(minimum_age=18).strftime("%Y-%m-%d"),
        }

        get_user_personal_information_mock.return_value = user_data

        db = MagicMock()
        response = await users_routes.get_user_personal_information(user_id, db)
        response_body = json.loads(response.body)

        self.assertEqual(response.status_code, 200)
        get_user_personal_information_mock.assert_called_once_with(user_id)
        self.assertEqual(response_body, user_data)

    @patch("app.services.users.UsersService.get_user_sports_information")
    async def test_get_user_sports_information(self, get_user_sports_information_mock):
        user_id = fake.uuid4()
        user_sports_profile_data = {
            "favourite_sport_id": str(fake.uuid4()),
            "training_objective": fake.enum(TrainingObjective).value,
            "weight": fake.random_int(min=1, max=100),
            "height": fake.random_int(min=1, max=100),
            "available_training_hours": fake.random_int(min=1, max=100),
            "training_frequency": fake.enum(TrainingFrequency).value,
        }

        get_user_sports_information_mock.return_value = user_sports_profile_data

        db = MagicMock()
        response = await users_routes.get_user_sports_information(user_id, db)
        response_body = json.loads(response.body)

        self.assertEqual(response.status_code, 200)
        get_user_sports_information_mock.assert_called_once_with(user_id)
        self.assertEqual(response_body, user_sports_profile_data)

    @patch("app.services.users.UsersService.get_user_nutritional_information")
    async def test_get_user_nutritional_information(self, get_user_nutritional_information_mock):
        user_id = fake.uuid4()
        user_sports_profile_data = {
            "food_preference": fake.enum(FoodPreference).value,
            "nutritional_limitations": [str(fake.uuid4()) for _ in range(fake.random_int(min=1, max=5))],
        }

        get_user_nutritional_information_mock.return_value = user_sports_profile_data

        db = MagicMock()
        response = await users_routes.get_user_nutritional_information(user_id, db)
        response_body = json.loads(response.body)

        self.assertEqual(response.status_code, 200)
        get_user_nutritional_information_mock.assert_called_once_with(user_id)
        self.assertEqual(response_body, user_sports_profile_data)

    @patch("app.services.users.UsersService.get_nutritional_limitations")
    async def test_get_nutritional_limitations(self, get_nutritional_limitations_mock):
        nutritional_limitations = [
            {
                "limitation_id": str(fake.uuid4()),
                "name": fake.word(),
                "description": fake.sentence(),
            },
            {
                "limitation_id": str(fake.uuid4()),
                "name": fake.word(),
                "description": fake.sentence(),
            },
            {
                "limitation_id": str(fake.uuid4()),
                "name": fake.word(),
                "description": fake.sentence(),
            },
        ]

        get_nutritional_limitations_mock.return_value = nutritional_limitations

        db = MagicMock()
        response = await users_routes.get_nutritional_limitations(db)
        response_body = json.loads(response.body)

        self.assertEqual(response.status_code, 200)
        get_nutritional_limitations_mock.assert_called_once()
        self.assertEqual(response_body, nutritional_limitations)

    @patch("app.services.users.UsersService.update_user_personal_information")
    async def test_update_user_personal_profile(self, update_user_personal_information_mock):
        user_id = fake.uuid4()
        user_updated_personal_profile = generate_random_user_personal_profile(fake)

        personal_profile_output = {
            "email": fake.email(),
            "first_name": fake.first_name(),
            "last_name": fake.last_name(),
            "identification_type": fake.enum(UserIdentificationType).value,
            "identification_number": fake.numerify(text="############"),
            "gender": fake.enum(Gender).value,
            "country_of_birth": fake.country(),
            "city_of_birth": fake.city(),
            "country_of_residence": fake.country(),
            "city_of_residence": fake.city(),
            "residence_age": fake.random_int(min=1, max=100),
            "birth_date": fake.date_of_birth(minimum_age=18).strftime("%Y-%m-%d"),
        }

        update_user_personal_information_mock.return_value = personal_profile_output

        db = MagicMock()
        response = await users_routes.update_user_personal_information(user_id, user_updated_personal_profile, db)
        response_body = json.loads(response.body)

        self.assertEqual(response.status_code, 200)
        update_user_personal_information_mock.assert_called_once()
        self.assertEqual(response_body, personal_profile_output)

    @patch("app.services.users.UsersService.update_user_sports_information")
    async def test_update_user_sports_profile(self, update_user_sports_information_mock):
        user_id = fake.uuid4()
        user_updated_sports_profile = generate_random_user_sports_profile(fake)

        sports_profile_output = {
            "favourite_sport_id": str(fake.uuid4()),
            "training_objective": fake.enum(TrainingObjective).value,
            "weight": fake.random_int(min=1, max=100),
            "height": fake.random_int(min=1, max=100),
            "available_training_hours": fake.random_int(min=1, max=100),
            "training_frequency": fake.enum(TrainingFrequency).value,
        }

        update_user_sports_information_mock.return_value = sports_profile_output

        db = MagicMock()
        response = await users_routes.update_user_sports_information(user_id, user_updated_sports_profile, db)
        response_body = json.loads(response.body)

        self.assertEqual(response.status_code, 200)
        update_user_sports_information_mock.assert_called_once()
        self.assertEqual(response_body, sports_profile_output)

    @patch("app.services.users.UsersService.update_user_nutritional_information")
    async def test_update_user_nutritional_profile(self, update_user_nutritional_information_mock):
        user_id = fake.uuid4()
        user_updated_nutritional_profile = generate_random_user_nutritional_profile(fake)

        nutritional_profile_output = [
            {
                "limitation_id": str(fake.uuid4()),
                "name": fake.word(),
                "description": fake.sentence(),
            },
            {
                "limitation_id": str(fake.uuid4()),
                "name": fake.word(),
                "description": fake.sentence(),
            },
            {
                "limitation_id": str(fake.uuid4()),
                "name": fake.word(),
                "description": fake.sentence(),
            },
        ]

        update_user_nutritional_information_mock.return_value = nutritional_profile_output

        db = MagicMock()
        response = await users_routes.update_user_nutritional_information(user_id, user_updated_nutritional_profile, db)
        response_body = json.loads(response.body)

        self.assertEqual(response.status_code, 200)
        update_user_nutritional_information_mock.assert_called_once()
        self.assertEqual(response_body, nutritional_profile_output)
