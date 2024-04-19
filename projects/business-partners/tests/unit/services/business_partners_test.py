import unittest

from unittest.mock import MagicMock, patch

from faker import Faker
from sqlalchemy.orm import Session

from app.models.mappers.user_mapper import DataClassMapper
from app.services.business_partners import BusinessPartnersService
from app.exceptions.exceptions import InvalidCredentialsError, EntityExistsError

from tests.utils.business_partners_util import (
    generate_random_user_login_data,
    generate_random_business_partner_create_data,
    generate_random_business_partner,
    generate_random_business_partner_product_create_data,
    generate_random_business_partner_product,
)

fake = Faker()


class TestBusinessPartnersService(unittest.TestCase):
    def setUp(self):
        self.mock_jwt = MagicMock()
        self.mock_aws_service = MagicMock()
        self.mock_db = MagicMock(spec=Session)
        self.business_partners_service = BusinessPartnersService(db=self.mock_db)
        self.business_partners_service.jwt_manager = self.mock_jwt
        self.business_partners_service.aws_service = self.mock_aws_service

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
        business_partner_data = generate_random_business_partner_create_data(fake)

        mock_query = MagicMock()
        mock_filter = MagicMock()

        self.mock_db.query.return_value = mock_query
        mock_query.filter.return_value = mock_filter
        mock_filter.first.return_value = business_partner_data

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

    def test_create_business_partner_product(self):
        business_partner = generate_random_business_partner(fake)

        mock_query = MagicMock()
        mock_filter = MagicMock()

        self.mock_db.query.return_value = mock_query
        mock_query.filter.return_value = mock_filter
        mock_filter.first.return_value = business_partner

        product_data = generate_random_business_partner_product_create_data(fake)

        response = self.business_partners_service.create_business_partner_product(product_data, business_partner.business_partner_id)

        self.assertEqual(response["category"], product_data.category.value)
        self.assertEqual(response["name"], product_data.name)
        self.assertEqual(response["summary"], product_data.summary)
        self.assertEqual(response["url"], product_data.url)
        self.assertEqual(response["price"], product_data.price)
        self.assertEqual(response["payment_type"], product_data.payment_type.value)
        self.assertEqual(response["payment_frequency"], product_data.payment_frequency.value)
        self.assertEqual(response["image_url"], product_data.image_url)
        self.assertEqual(response["description"], product_data.description)

    @patch("tempfile.NamedTemporaryFile")
    def test_create_business_partner_product_base64_image(self, named_tempfile_mock):
        business_partner = generate_random_business_partner(fake)

        mock_query = MagicMock()
        mock_filter = MagicMock()

        self.mock_db.query.return_value = mock_query
        mock_query.filter.return_value = mock_filter
        mock_filter.first.return_value = business_partner

        fake_s3_url = f"https://{fake.word()}.s3.{fake.word()}.amazonaws.com/{fake.word()}"
        self.mock_aws_service.s3.upload_file.return_value = fake_s3_url
        tmp_file_mock = MagicMock()
        tmp_file_mock.write.return_value = None
        named_tempfile_mock.side_effect = tmp_file_mock

        product_data = generate_random_business_partner_product_create_data(fake)
        product_data.image_base64 = f"data:image/png;base64,{fake.sha256()}"

        response = self.business_partners_service.create_business_partner_product(product_data, business_partner.business_partner_id)

        self.assertEqual(response["category"], product_data.category.value)
        self.assertEqual(response["name"], product_data.name)
        self.assertEqual(response["summary"], product_data.summary)
        self.assertEqual(response["url"], product_data.url)
        self.assertEqual(response["price"], product_data.price)
        self.assertEqual(response["payment_type"], product_data.payment_type.value)
        self.assertEqual(response["payment_frequency"], product_data.payment_frequency.value)
        self.assertEqual(response["image_url"], fake_s3_url)
        self.assertEqual(response["description"], product_data.description)

    def test_create_business_partner_product_business_partner_not_found(self):
        business_partner_id = fake.uuid4()
        mock_query = MagicMock()
        mock_filter = MagicMock()

        self.mock_db.query.return_value = mock_query
        mock_query.filter.return_value = mock_filter
        mock_filter.first.return_value = None

        product_data = generate_random_business_partner_product_create_data(fake)

        with self.assertRaises(Exception) as context:
            self.business_partners_service.create_business_partner_product(product_data, business_partner_id)
        self.assertEqual(str(context.exception), f"Business partner with id {business_partner_id} not found")

    def test_get_business_partner_products(self):
        business_partner_id = fake.uuid4()
        mock_query = MagicMock()
        mock_filter = MagicMock()
        mock_limit = MagicMock()
        mock_offset = MagicMock()

        business_partner = generate_random_business_partner(fake)
        products = [generate_random_business_partner_product(fake) for _ in range(3)]

        self.mock_db.query.return_value = mock_query
        mock_query.filter.return_value = mock_filter
        mock_filter.first.return_value = business_partner
        mock_filter.limit.return_value = mock_limit
        mock_limit.offset.return_value = mock_offset
        mock_offset.all.return_value = products

        response = self.business_partners_service.get_business_partner_products(business_partner_id, 0, 3)

        self.assertEqual(len(response), 3)
        for product in response:
            self.assertIn("product_id", product)
            self.assertIn("category", product)
            self.assertIn("name", product)
            self.assertIn("summary", product)
            self.assertIn("url", product)
            self.assertIn("price", product)
            self.assertIn("payment_type", product)
            self.assertIn("payment_frequency", product)
            self.assertIn("image_url", product)
            self.assertIn("description", product)

    def test_get_business_partner_products_business_partner_not_found(self):
        business_partner_id = fake.uuid4()
        mock_query = MagicMock()
        mock_filter = MagicMock()

        self.mock_db.query.return_value = mock_query
        mock_query.filter.return_value = mock_filter
        mock_filter.first.return_value = None

        with self.assertRaises(Exception) as context:
            self.business_partners_service.get_business_partner_products(business_partner_id, 0, 3)
        self.assertEqual(str(context.exception), f"Business partner with id {business_partner_id} not found")

    def test_get_all_offered_business_partners_products(self):
        business_partner_id = fake.uuid4()
        mock_query = MagicMock()
        mock_filter = MagicMock()
        mock_limit = MagicMock()
        mock_offset = MagicMock()

        business_partner = generate_random_business_partner(fake)
        products = [generate_random_business_partner_product(fake) for _ in range(3)]

        self.mock_db.query.return_value = mock_query
        mock_query.filter.return_value = mock_filter
        mock_filter.first.return_value = business_partner
        mock_filter.limit.return_value = mock_limit
        mock_limit.offset.return_value = mock_offset
        mock_offset.all.return_value = products[1:3]

        response = self.business_partners_service.get_all_offered_products(0, 3)

        self.assertEqual(len(response), 2)
        for product in response:
            self.assertIn("product_id", product)
            self.assertIn("category", product)
            self.assertIn("name", product)
            self.assertIn("summary", product)
            self.assertIn("url", product)
            self.assertIn("price", product)
            self.assertIn("payment_type", product)
            self.assertIn("payment_frequency", product)
            self.assertIn("image_url", product)
            self.assertIn("description", product)
            self.assertTrue(product["active"])

    def test_update_business_partner_product(self):
        business_partner = generate_random_business_partner(fake)
        existing_product = generate_random_business_partner_product(fake)
        existing_product.business_partner_id = business_partner.business_partner_id

        mock_query = MagicMock()
        mock_filter = MagicMock()

        self.mock_db.query.return_value = mock_query
        mock_query.filter.return_value = mock_filter
        mock_filter.first.side_effect = [business_partner, existing_product]

        updated_product_data = generate_random_business_partner_product_create_data(fake)
        updated_product_data.active = False

        response = self.business_partners_service.update_business_partner_product(existing_product.product_id, business_partner.business_partner_id, updated_product_data)

        self.assertEqual(response["category"], updated_product_data.category.value)
        self.assertEqual(response["name"], updated_product_data.name)
        self.assertEqual(response["summary"], updated_product_data.summary)
        self.assertEqual(response["url"], updated_product_data.url)
        self.assertEqual(response["price"], updated_product_data.price)
        self.assertEqual(response["payment_type"], updated_product_data.payment_type.value)
        self.assertEqual(response["payment_frequency"], updated_product_data.payment_frequency.value)
        self.assertEqual(response["image_url"], updated_product_data.image_url)
        self.assertEqual(response["description"], updated_product_data.description)
        self.assertFalse(response["active"])

    @patch("tempfile.NamedTemporaryFile")
    def test_update_business_partner_product_base64_image(self, named_tempfile_mock):
        business_partner = generate_random_business_partner(fake)
        existing_product = generate_random_business_partner_product(fake)
        existing_product.business_partner_id = business_partner.business_partner_id

        mock_query = MagicMock()
        mock_filter = MagicMock()

        self.mock_db.query.return_value = mock_query
        mock_query.filter.return_value = mock_filter
        mock_filter.first.side_effect = [business_partner, existing_product]

        fake_s3_url = f"https://{fake.word()}.s3.{fake.word()}.amazonaws.com/{fake.word()}"
        self.mock_aws_service.s3.upload_file.return_value = fake_s3_url
        tmp_file_mock = MagicMock()
        tmp_file_mock.write.return_value = None
        named_tempfile_mock.side_effect = tmp_file_mock

        updated_product_data = generate_random_business_partner_product_create_data(fake)
        updated_product_data.image_base64 = f"data:image/png;base64,{fake.sha256()}"

        response = self.business_partners_service.update_business_partner_product(
            existing_product.product_id,
            business_partner.business_partner_id,
            updated_product_data,
        )

        self.assertEqual(response["category"], updated_product_data.category.value)
        self.assertEqual(response["name"], updated_product_data.name)
        self.assertEqual(response["summary"], updated_product_data.summary)
        self.assertEqual(response["url"], updated_product_data.url)
        self.assertEqual(response["price"], updated_product_data.price)
        self.assertEqual(response["payment_type"], updated_product_data.payment_type.value)
        self.assertEqual(response["payment_frequency"], updated_product_data.payment_frequency.value)
        self.assertEqual(response["image_url"], fake_s3_url)
        self.assertEqual(response["description"], updated_product_data.description)

    def test_update_business_partner_product_partner_not_found(self):
        business_partner_id = fake.uuid4()
        product_id = fake.uuid4()
        updated_product = generate_random_business_partner_create_data(fake)
        mock_query = MagicMock()
        mock_filter = MagicMock()

        self.mock_db.query.return_value = mock_query
        mock_query.filter.return_value = mock_filter
        mock_filter.first.return_value = None

        with self.assertRaises(Exception) as context:
            self.business_partners_service.update_business_partner_product(product_id, business_partner_id, updated_product)
        self.assertEqual(str(context.exception), f"Business partner with id {business_partner_id} not found")

    def test_update_business_partner_product_product_not_found(self):
        business_partner = generate_random_business_partner(fake)
        product_id = fake.uuid4()
        updated_product = generate_random_business_partner_create_data(fake)
        mock_query = MagicMock()
        mock_filter = MagicMock()

        self.mock_db.query.return_value = mock_query
        mock_query.filter.return_value = mock_filter
        mock_filter.first.side_effect = [business_partner, None]

        with self.assertRaises(Exception) as context:
            self.business_partners_service.update_business_partner_product(product_id, business_partner.business_partner_id, updated_product)
        self.assertEqual(str(context.exception), f"Product with id {product_id} not found")

    def test_delete_business_partner_product(self):
        business_partner = generate_random_business_partner(fake)
        existing_product = generate_random_business_partner_product(fake)
        existing_product.business_partner_id = business_partner.business_partner_id

        mock_query = MagicMock()
        mock_filter = MagicMock()

        self.mock_db.query.return_value = mock_query
        mock_query.filter.return_value = mock_filter
        mock_filter.first.side_effect = [business_partner, existing_product]

        response = self.business_partners_service.delete_business_partner_product(
            existing_product.product_id,
            business_partner.business_partner_id,
        )

        self.assertEqual(response["message"], "Product deleted")

    def test_delete_business_partner_product_partner_not_found(self):
        business_partner_id = fake.uuid4()
        product_id = fake.uuid4()
        mock_query = MagicMock()
        mock_filter = MagicMock()

        self.mock_db.query.return_value = mock_query
        mock_query.filter.return_value = mock_filter
        mock_filter.first.return_value = None

        with self.assertRaises(Exception) as context:
            self.business_partners_service.delete_business_partner_product(product_id, business_partner_id)
        self.assertEqual(str(context.exception), f"Business partner with id {business_partner_id} not found")

    def test_delete_business_partner_product_product_not_found(self):
        business_partner = generate_random_business_partner(fake)
        product_id = fake.uuid4()
        mock_query = MagicMock()
        mock_filter = MagicMock()

        self.mock_db.query.return_value = mock_query
        mock_query.filter.return_value = mock_filter
        mock_filter.first.side_effect = [business_partner, None]

        with self.assertRaises(Exception) as context:
            self.business_partners_service.delete_business_partner_product(product_id, business_partner.business_partner_id)
        self.assertEqual(str(context.exception), f"Product with id {product_id} not found")
