import unittest
from unittest.mock import patch

from faker import Faker

from app.models.schemas.schema import PaymentData
from app.services.external import ExternalServices

fake = Faker()


class TestExternalServices(unittest.TestCase):

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
