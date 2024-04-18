import unittest

from faker import Faker

from app.exceptions.exceptions import InvalidValueError
from app.models.schemas.schema import BusinessPartnerCredentials, CreateBusinessPartnerProduct
from app.models.business_partners import ProductCategory, PaymentType, PaymentFrequency

fake = Faker()


class TestUserCredentials(unittest.TestCase):
    def test_valid_credentials_email_password(self):
        email = fake.email()
        password = fake.password(length=12, special_chars=True, digits=True, upper_case=True, lower_case=True)

        credentials = {"email": email, "password": password}

        credentials = BusinessPartnerCredentials(**credentials)
        self.assertEqual(credentials.email, email)
        self.assertEqual(credentials.password, password)

    def test_valid_credentials_token(self):
        token = fake.word()

        credentials = {"refresh_token": token}

        credentials = BusinessPartnerCredentials(**credentials)
        self.assertEqual(credentials.refresh_token, token)

    def test_invalid_credentials(self):
        email = fake.email()

        # Invalid credentials scenarios
        # 1. Providing refresh_token along with email and password
        with self.assertRaises(InvalidValueError) as context:
            BusinessPartnerCredentials(refresh_token="refresh_token", email=email, password=fake.password())
        self.assertEqual(str(context.exception), "Cannot provide refresh_token along with email and password")

        # 2. Not providing refresh_token or both email and password
        with self.assertRaises(InvalidValueError) as context:
            BusinessPartnerCredentials(email=email)
        self.assertEqual(str(context.exception), "Either provide refresh_token or both email and password")

        # 3. Not providing any data
        with self.assertRaises(InvalidValueError) as context:
            BusinessPartnerCredentials()
        self.assertEqual(str(context.exception), "Either provide refresh_token or both email and password")

    def test_create_business_partner_product_no_image(self):
        product_data = {
            "product_id": fake.uuid4(),
            "business_partner_id": fake.uuid4(),
            "category": fake.enum(ProductCategory),
            "name": fake.word(),
            "url": fake.url(),
            "price": fake.random_number(),
            "payment_type": fake.enum(PaymentType),
            "payment_frequency": fake.enum(PaymentFrequency),
            "description": fake.text(),
        }

        with self.assertRaises(InvalidValueError) as context:
            CreateBusinessPartnerProduct(**product_data)
        self.assertEqual(str(context.exception), "Provide either image_url or image_base64")

    def test_create_business_partner_product_with_url_and_base64(self):
        product_data = {
            "product_id": fake.uuid4(),
            "business_partner_id": fake.uuid4(),
            "category": fake.enum(ProductCategory),
            "name": fake.word(),
            "url": fake.url(),
            "price": fake.random_number(),
            "payment_type": fake.enum(PaymentType),
            "payment_frequency": fake.enum(PaymentFrequency),
            "image_url": fake.url(),
            "image_base64": fake.word(),
            "description": fake.text(),
        }

        with self.assertRaises(InvalidValueError) as context:
            CreateBusinessPartnerProduct(**product_data)
        self.assertEqual(str(context.exception), "Cannot provide both image_url and image_base64")
