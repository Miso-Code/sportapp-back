import unittest

from unittest.mock import patch

from faker import Faker

from app.models.schemas.schema import PaymentData
from app.models.users import FoodPreference, TrainingObjective
from app.services.external import ExternalServices
from app.exceptions.exceptions import NotFoundError, ExternalServiceError

fake = Faker()


class TestExternalService(unittest.TestCase):

    @patch("requests.get")
    def test_get_sport(self, mock_get):
        user_id = fake.uuid4()
        user_token = f"Bearer {fake.sha256()}"
        external_service = ExternalServices()
        mock_get.return_value.status_code = 200
        mock_get.return_value.json.return_value = {"id": user_id}

        response = external_service.get_sport(user_id, user_token)

        self.assertEqual(response, {"id": user_id})
        self.assertTrue(mock_get.called)

    @patch("requests.get")
    def test_get_sport_not_found(self, mock_get):
        user_id = fake.uuid4()
        user_token = f"Bearer {fake.sha256()}"
        external_service = ExternalServices()
        mock_get.return_value.status_code = 404

        with self.assertRaises(NotFoundError) as context:
            external_service.get_sport(user_id, user_token)

        self.assertEqual(str(context.exception), f"Sport with id {user_id} not found")

    @patch("requests.get")
    def test_get_sport_none_token(self, mock_get):
        user_id = fake.uuid4()
        external_service = ExternalServices()

        with self.assertRaises(NotFoundError) as context:
            external_service.get_sport(user_id, None)

        self.assertEqual(str(context.exception), f"Sport with id {user_id} not found")

    @patch("requests.post")
    def test_create_training_plan(self, mock_post):
        user_token = f"Bearer {fake.sha256()}"
        training_plan_data = {
            "training_objective": fake.random.choice(["weight_loss", "muscle_gain"]),
            "available_training_hours": fake.random_int(min=1, max=24),
            "available_weekdays": list(set([fake.day_of_week().lower() for _ in range(fake.random_int(min=1, max=7))])),
            "preferred_training_start_time": fake.time(pattern="%I:%M %p"),
            "favourite_sport_id": fake.uuid4(),
            "weight": fake.random_int(min=1, max=200),
            "height": fake.random_int(min=1, max=200),
            "training_limitations": [{"name": fake.word(), "description": fake.sentence()} for _ in range(fake.random_int(min=1, max=5))],
        }
        external_service = ExternalServices()
        mock_post.return_value.status_code = 200
        mock_post.return_value.json.return_value = training_plan_data

        response = external_service.create_training_plan(training_plan_data, user_token)

        self.assertEqual(response, training_plan_data)
        self.assertTrue(mock_post.called)

    @patch("requests.post")
    def test_create_training_plan_invalid_data(self, mock_post):
        user_token = f"Bearer {fake.sha256()}"
        training_plan_data = {
            "training_objective": fake.word(),
            "available_training_hours": fake.word(),
            "available_weekdays": [fake.word(), fake.word(), fake.word()],
            "preferred_training_start_time": fake.word(),
            "favourite_sport_id": fake.word(),
            "weight": fake.word(),
            "height": fake.word(),
            "training_limitations": [{"name": fake.word(), "description": fake.word()} for _ in range(fake.random_int(min=1, max=5))],
        }
        external_service = ExternalServices()
        mock_post.return_value.status_code = 400

        with self.assertRaises(NotFoundError) as context:
            external_service.create_training_plan(training_plan_data, user_token)

        self.assertEqual(str(context.exception), "Failed to create training plan")
        self.assertTrue(mock_post.called)

    @patch("requests.post")
    def test_create_training_plan_none_token(self, mock_post):
        training_plan_data = {
            "training_objective": fake.random.choice(["weight_loss", "muscle_gain"]),
            "available_training_hours": fake.random_int(min=1, max=24),
            "available_weekdays": list(set([fake.day_of_week().lower() for _ in range(fake.random_int(min=1, max=7))])),
            "preferred_training_start_time": fake.time(pattern="%I:%M %p"),
            "favourite_sport_id": fake.uuid4(),
            "weight": fake.random_int(min=1, max=200),
            "height": fake.random_int(min=1, max=200),
            "training_limitations": [{"name": fake.word(), "description": fake.sentence()} for _ in range(fake.random_int(min=1, max=5))],
        }
        external_service = ExternalServices()

        with self.assertRaises(NotFoundError) as context:
            external_service.create_training_plan(training_plan_data, None)

        self.assertEqual(str(context.exception), "Failed to create training plan")
        self.assertTrue(mock_post.called)

    @patch("requests.post")
    def test_process_payment_success(self, mock_post):
        payment_data = PaymentData(
            card_number=fake.credit_card_number(),
            card_holder=fake.name(),
            card_expiration_date=fake.credit_card_expire(),
            card_cvv=fake.credit_card_security_code(),
            amount=fake.random_number(digits=5),
        )

        mock_post.return_value.status_code = 200

        response = ExternalServices().process_payment(payment_data)

        self.assertTrue(response[0])
        self.assertEqual(response[1], {})

    @patch("requests.post")
    def test_process_payment_failure(self, mock_post):
        payment_data = PaymentData(
            card_number=fake.credit_card_number(),
            card_holder=fake.name(),
            card_expiration_date=fake.credit_card_expire(),
            card_cvv=fake.credit_card_security_code(),
            amount=fake.random_number(digits=5),
        )

        mock_post.return_value.status_code = 400
        mock_post.return_value.json.return_value = {"error": "Invalid card number"}

        response = ExternalServices().process_payment(payment_data)

        self.assertFalse(response[0])
        self.assertEqual(response[1], {"error": "Invalid card number"})

    @patch("requests.post")
    def test_process_payment_apikey_error(self, mock_post):
        payment_data = PaymentData(
            card_number=fake.credit_card_number(),
            card_holder=fake.name(),
            card_expiration_date=fake.credit_card_expire(),
            card_cvv=fake.credit_card_security_code(),
            amount=fake.random_number(digits=5),
        )

        mock_post.return_value.status_code = 401

        with self.assertRaises(ExternalServiceError) as context:
            response = ExternalServices().process_payment(payment_data)
        self.assertEqual(str(context.exception), "Miso Stripe API key is invalid")

    @patch("requests.post")
    def test_create_nutritional_plan(self, mock_post):
        user_data = {
            "age": fake.random_int(min=18, max=50),
            "gender": fake.random.choice(["M", "F", "O"]),
            "training_objective": fake.enum(TrainingObjective).value,
            "weight": fake.random_int(min=1, max=200),
            "height": fake.random_int(min=1, max=200),
            "food_preference": fake.enum(FoodPreference).value,
            "training_limitations": [{"name": fake.word(), "description": fake.sentence()} for _ in range(fake.random_int(min=1, max=5))],
        }
        user_token = f"Bearer {fake.sha256()}"
        external_service = ExternalServices()
        mock_post.return_value.status_code = 201
        mock_post.return_value.json.return_value = user_data

        response = external_service.create_nutritional_plan(user_data, user_token)

        self.assertEqual(response, user_data)
        self.assertTrue(mock_post.called)

    @patch("requests.post")
    def test_create_nutritional_plan_error(self, mock_post):
        user_data = {
            "age": fake.random_int(min=18, max=50),
            "gender": fake.random.choice(["M", "F", "O"]),
            "training_objective": fake.enum(TrainingObjective).value,
            "weight": fake.random_int(min=1, max=200),
            "height": fake.random_int(min=1, max=200),
            "food_preference": fake.enum(FoodPreference).value,
            "training_limitations": [{"name": fake.word(), "description": fake.sentence()} for _ in range(fake.random_int(min=1, max=5))],
        }

        user_token = f"Bearer {fake.sha256()}"
        external_service = ExternalServices()
        mock_post.return_value.status_code = 400
        mock_post.return_value.json.return_value = user_data

        with self.assertRaises(ExternalServiceError) as context:
            external_service.create_nutritional_plan(user_data, user_token)
        self.assertEqual(str(context.exception), "Failed to create nutritional plan")
