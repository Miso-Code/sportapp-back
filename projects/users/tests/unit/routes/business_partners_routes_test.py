import json
import unittest

from unittest.mock import patch, MagicMock

from faker import Faker

from app.models.schemas.schema import UserCredentials, BusinessPartnerCreate
from app.routes import business_partners_routes

fake = Faker()


class TestUsersRoutes(unittest.IsolatedAsyncioTestCase):

    @patch("app.services.business_partners.BusinessPartnersService.create_business_partner")
    async def test_register_business_partner(self, mock_create_business_partner):
        business_partner_create = BusinessPartnerCreate(business_partner_name=fake.company(), email=fake.email(), password=fake.password())
        db_mock = MagicMock()

        business_partner_created_dict = {
            "business_partner_id": fake.uuid4(),
            "business_partner_name": fake.name(),
            "email": business_partner_create.email,
        }

        mock_create_business_partner.return_value = business_partner_created_dict

        response = await business_partners_routes.register_business_partner(business_partner_create, db_mock)
        response_body = json.loads(response.body)

        mock_create_business_partner.assert_called_once_with(business_partner_create)
        self.assertEqual(response.status_code, 201)
        self.assertEqual(response_body, business_partner_created_dict)

    @patch("app.services.business_partners.BusinessPartnersService.authenticate_business_partner")
    async def test_login_business_partner(self, mock_authenticate_business_partner):
        business_partner_credentials = UserCredentials(email=fake.email(), password=fake.password())
        db_mock = MagicMock()

        token_data = {
            "access_token": fake.sha256(),
            "access_token_expires_minutes": fake.random_int(min=1, max=60),
            "refresh_token": fake.sha256(),
            "refresh_token_expires_minutes": fake.random_int(min=1, max=60),
        }

        mock_authenticate_business_partner.return_value = token_data

        response = await business_partners_routes.login_business_partner(business_partner_credentials, db_mock)
        response_body = json.loads(response.body)

        mock_authenticate_business_partner.assert_called_once_with(business_partner_credentials)
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response_body, token_data)
