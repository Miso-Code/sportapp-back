import json
import unittest

from unittest.mock import patch, MagicMock

from faker import Faker

from app.models.mappers.data_mapper import DataClassMapper
from tests.utils.sport_events_util import generate_random_sport_event_data, generate_random_sport_event
from app.routes import sport_events_routes

fake = Faker()


class TestSportEventsRoutes(unittest.IsolatedAsyncioTestCase):

    @patch("app.services.sport_events.SportEventsService.create_sport_event")
    async def test_create_sport_event(self, mock_create_sport_event):
        sport_event_create = generate_random_sport_event_data(fake)
        sport_event = generate_random_sport_event(fake)
        db_mock = MagicMock()

        mock_create_sport_event.return_value = DataClassMapper.to_dict(sport_event)

        response = await sport_events_routes.create_sport_event(sport_event_create, db_mock)

        response_json = json.loads(response.body)

        self.assertEqual(response.status_code, 201)
        self.assertEqual(response_json["event_id"], str(sport_event.event_id))
        self.assertEqual(response_json["sport_id"], str(sport_event.sport_id))
        self.assertEqual(response_json["location_latitude"], sport_event.location_latitude)
        self.assertEqual(response_json["location_longitude"], sport_event.location_longitude)
        self.assertEqual(response_json["start_date"], sport_event.start_date.isoformat())
        self.assertEqual(response_json["end_date"], sport_event.end_date.isoformat())
        self.assertEqual(response_json["title"], sport_event.title)
        self.assertEqual(response_json["capacity"], sport_event.capacity)
        self.assertEqual(response_json["description"], sport_event.description)

    @patch("app.services.sport_events.SportEventsService.get_sport_events")
    async def test_get_sport_events(self, mock_get_sport_events):
        db_mock = MagicMock()
        limit = fake.random_int(min=1, max=20)
        offset = fake.random_int(min=0, max=10)

        sport_events = [DataClassMapper.to_dict(generate_random_sport_event(fake)) for _ in range(limit)]

        mock_get_sport_events.return_value = sport_events

        response = await sport_events_routes.get_sport_events(db_mock, None, offset, limit)
        response_json = json.loads(response.body)

        mock_get_sport_events.assert_called_once_with(None, offset, limit)
        self.assertEqual(response.status_code, 200)
        self.assertEqual(len(response_json), len(sport_events))
        for i in range(len(sport_events)):
            print(response_json[i])
            self.assertEqual(response_json[i]["event_id"], str(sport_events[i]["event_id"]))
            self.assertEqual(response_json[i]["sport_id"], str(sport_events[i]["sport_id"]))
            self.assertEqual(response_json[i]["location_latitude"], sport_events[i]["location_latitude"])
            self.assertEqual(response_json[i]["location_longitude"], sport_events[i]["location_longitude"])
            self.assertEqual(response_json[i]["start_date"], sport_events[i]["start_date"])
            self.assertEqual(response_json[i]["end_date"], sport_events[i]["end_date"])
            self.assertEqual(response_json[i]["title"], sport_events[i]["title"])
            self.assertEqual(response_json[i]["capacity"], sport_events[i]["capacity"])
            self.assertEqual(response_json[i]["description"], sport_events[i]["description"])

    @patch("app.services.sport_events.SportEventsService.get_sport_event")
    async def test_get_sport_event(self, mock_get_sport_event):
        db_mock = MagicMock()
        sport_event_id = fake.uuid4()
        sport_event = generate_random_sport_event(fake)

        mock_get_sport_event.return_value = DataClassMapper.to_dict(sport_event)

        response = await sport_events_routes.get_sport_event(sport_event_id, db_mock)
        response_json = json.loads(response.body)

        mock_get_sport_event.assert_called_once_with(sport_event_id)
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response_json["event_id"], str(sport_event.event_id))
        self.assertEqual(response_json["sport_id"], str(sport_event.sport_id))
        self.assertEqual(response_json["location_latitude"], sport_event.location_latitude)
        self.assertEqual(response_json["location_longitude"], sport_event.location_longitude)
        self.assertEqual(response_json["start_date"], sport_event.start_date.isoformat())
        self.assertEqual(response_json["end_date"], sport_event.end_date.isoformat())
        self.assertEqual(response_json["title"], sport_event.title)
        self.assertEqual(response_json["capacity"], sport_event.capacity)
        self.assertEqual(response_json["description"], sport_event.description)


# @patch("app.services.business_partners.BusinessPartnersService.create_business_partner")
# async def test_register_business_partner(self, mock_create_business_partner):
#     business_partner_create = BusinessPartnerCreate(business_partner_name=fake.company(), email=fake.email(), password=fake.password())
#     db_mock = MagicMock()
#
#     business_partner_created_dict = {
#         "business_partner_id": fake.uuid4(),
#         "business_partner_name": fake.name(),
#         "email": business_partner_create.email,
#     }
#
#     mock_create_business_partner.return_value = business_partner_created_dict
#
#     response = await business_partners_routes.register_business_partner(business_partner_create, db_mock)
#     response_body = json.loads(response.body)
#
#     mock_create_business_partner.assert_called_once_with(business_partner_create)
#     self.assertEqual(response.status_code, 201)
#     self.assertEqual(response_body, business_partner_created_dict)
#
# @patch("app.services.business_partners.BusinessPartnersService.authenticate_business_partner")
# async def test_login_business_partner(self, mock_authenticate_business_partner):
#     business_partner_credentials = BusinessPartnerCredentials(email=fake.email(), password=fake.password())
#     db_mock = MagicMock()
#
#     token_data = {
#         "access_token": fake.sha256(),
#         "access_token_expires_minutes": fake.random_int(min=1, max=60),
#         "refresh_token": fake.sha256(),
#         "refresh_token_expires_minutes": fake.random_int(min=1, max=60),
#     }
#
#     mock_authenticate_business_partner.return_value = token_data
#
#     response = await business_partners_routes.login_business_partner(business_partner_credentials, db_mock)
#     response_body = json.loads(response.body)
#
#     mock_authenticate_business_partner.assert_called_once_with(business_partner_credentials)
#     self.assertEqual(response.status_code, 200)
#     self.assertEqual(response_body, token_data)
#
# @patch("app.services.business_partners.BusinessPartnersService.create_business_partner_product")
# async def test_create_business_partner_product(self, mock_create_business_partner_product):
#     business_partner_product_create = generate_random_business_partner_product_create_data(fake)
#     business_partner_product_create_dict = {
#         "product_id": fake.uuid4(),
#         "category": business_partner_product_create.category.value,
#         "name": business_partner_product_create.name,
#         "summary": fake.word(),
#         "url": business_partner_product_create.url,
#         "price": business_partner_product_create.price,
#         "payment_type": business_partner_product_create.payment_type.value,
#         "payment_frequency": business_partner_product_create.payment_frequency.value,
#         "image_url": business_partner_product_create.image_url,
#         "description": business_partner_product_create.description,
#     }
#     db_mock = MagicMock()
#
#     mock_create_business_partner_product.return_value = business_partner_product_create_dict
#
#     response = await business_partners_routes.create_business_partner_product(business_partner_product_create, db_mock)
#
#     response_json = json.loads(response.body)
#
#     self.assertEqual(response.status_code, 201)
#     self.assertEqual(response_json, business_partner_product_create_dict)
#
# @patch("app.services.business_partners.BusinessPartnersService.update_business_partner_product")
# async def test_update_business_partner_product(self, update_product_mock):
#     product_id = fake.uuid4()
#     partner_id = fake.uuid4()
#     business_partner_product_update = generate_random_business_partner_product_create_data(fake)
#     business_partner_product_update_dict = {
#         "category": business_partner_product_update.category.value,
#         "name": business_partner_product_update.name,
#         "summary": fake.word(),
#         "url": business_partner_product_update.url,
#         "price": business_partner_product_update.price,
#         "payment_type": business_partner_product_update.payment_type.value,
#         "payment_frequency": business_partner_product_update.payment_frequency.value,
#         "image_url": business_partner_product_update.image_url,
#         "description": business_partner_product_update.description,
#     }
#     db_mock = MagicMock()
#
#     update_product_mock.return_value = business_partner_product_update_dict
#
#     response = await business_partners_routes.update_business_partner_product(product_id, business_partner_product_update, partner_id, db_mock)
#
#     response_json = json.loads(response.body)
#
#     self.assertEqual(response.status_code, 200)
#     self.assertEqual(response_json, business_partner_product_update_dict)
#
# @patch("app.services.business_partners.BusinessPartnersService.get_business_partner_product")
# async def test_get_business_partner_product(self, get_product_mock):
#     db_mock = MagicMock()
#     product_id = fake.uuid4()
#     business_partner_id = fake.uuid4()
#     business_partner_product_update = generate_random_business_partner_product_create_data(fake)
#     business_partner_product_update_dict = {
#         "category": business_partner_product_update.category.value,
#         "name": business_partner_product_update.name,
#         "summary": fake.word(),
#         "url": business_partner_product_update.url,
#         "price": business_partner_product_update.price,
#         "payment_type": business_partner_product_update.payment_type.value,
#         "payment_frequency": business_partner_product_update.payment_frequency.value,
#         "image_url": business_partner_product_update.image_url,
#         "description": business_partner_product_update.description,
#     }
#
#     get_product_mock.return_value = business_partner_product_update_dict
#
#     response = await business_partners_routes.get_business_partner_product(product_id, business_partner_id, db_mock)
#     response_json = json.loads(response.body)
#
#     get_product_mock.assert_called_once_with(product_id, business_partner_id)
#     self.assertEqual(response.status_code, 200)
#     self.assertEqual(response_json, business_partner_product_update_dict)
#
# @patch("app.services.business_partners.BusinessPartnersService.delete_business_partner_product")
# async def test_delete_business_partner_product(self, delete_product_mock):
#     db_mock = MagicMock()
#     product_id = fake.uuid4()
#     business_partner_id = fake.uuid4()
#
#     delete_response = {"message": "Product Deleted"}
#     delete_product_mock.return_value = delete_response
#
#     response = await business_partners_routes.delete_business_partner_product(product_id, business_partner_id, db_mock)
#
#     response_json = json.loads(response.body)
#
#     self.assertEqual(response.status_code, 200)
#     self.assertEqual(response_json, delete_response)
#
# @patch("app.services.business_partners.BusinessPartnersService.purchase_product")
# async def test_purchase_business_partner_product(self, purchase_product_mock):
#     db_mock = MagicMock()
#     product_id = fake.uuid4()
#     business_partner_id = fake.uuid4()
#
#     purchase_response = {"message": "Product Purchased"}
#     purchase_product_mock.return_value = purchase_response
#
#     product_purchase = generate_random_product_purchase(fake)
#
#     response = await business_partners_routes.purchase_product(product_id, product_purchase, business_partner_id, db_mock)
#
#     response_json = json.loads(response.body)
#
#     self.assertEqual(response.status_code, 200)
#     self.assertEqual(response_json, purchase_response)
#
# @patch("app.services.business_partners.BusinessPartnersService.get_products_transactions")
# async def test_get_products_transactions(self, get_products_transactions_mock):
#     db_mock = MagicMock()
#     product_id = fake.uuid4()
#     business_partner_id = fake.uuid4()
#     limit = fake.random_int(min=1, max=20)
#     offset = fake.random_int(min=0, max=10)
#
#     transactions = [DataClassMapper.to_dict(generate_random_product_transaction(fake)) for _ in range(limit)]
#
#     get_products_transactions_mock.return_value = transactions
#
#     response = await business_partners_routes.get_products_transactions(business_partner_id, db_mock, offset, limit)
#     response_json = json.loads(response.body)
#
#     get_products_transactions_mock.assert_called_once_with(business_partner_id, offset, limit)
#     self.assertEqual(response.status_code, 200)
#     self.assertEqual(len(response_json), len(transactions))
#
# @patch("app.services.business_partners.BusinessPartnersService.get_business_partner_products")
# async def test_get_all_business_partner_products(self, mock_get_business_partner_products):
#     db_mock = MagicMock()
#     user_id = fake.uuid4()
#     limit = fake.random_int(min=1, max=20)
#     offset = fake.random_int(min=0, max=10)
#
#     business_partner_products = [
#         {
#             "product_id": fake.uuid4(),
#             "category": fake.random_element(["product", "service"]),
#             "name": fake.company(),
#             "summary": fake.word(),
#             "url": fake.url(),
#             "price": fake.random_int(min=1, max=1000),
#             "payment_type": fake.random_element(["one_time", "subscription"]),
#             "payment_frequency": fake.random_element(["monthly", "yearly"]),
#             "image_url": fake.url(),
#             "description": fake.text(),
#         }
#         for _ in range(limit)
#     ]
#
#     mock_get_business_partner_products.return_value = business_partner_products
#
#     response = await business_partners_routes.get_all_business_partner_products(user_id, db_mock, offset, limit)
#     response_json = json.loads(response.body)
#
#     mock_get_business_partner_products.assert_called_once_with(user_id, offset, limit)
#     self.assertEqual(response.status_code, 200)
#     self.assertEqual(response_json, business_partner_products)
#
# @patch("app.services.business_partners.BusinessPartnersService.get_all_offered_products")
# async def test_get_offered_business_partners_products(self, offered_products_mock):
#     db_mock = MagicMock()
#     limit = fake.random_int(min=1, max=20)
#     offset = fake.random_int(min=0, max=10)
#
#     business_partner_products = [
#         {
#             "product_id": fake.uuid4(),
#             "category": fake.random_element(["product", "service"]),
#             "name": fake.company(),
#             "summary": fake.word(),
#             "url": fake.url(),
#             "price": fake.random_int(min=1, max=1000),
#             "payment_type": fake.random_element(["one_time", "subscription"]),
#             "payment_frequency": fake.random_element(["monthly", "yearly"]),
#             "image_url": fake.url(),
#             "description": fake.text(),
#         }
#         for _ in range(limit)
#     ]
#
#     offered_products_mock.return_value = business_partner_products
#
#     response = await business_partners_routes.get_all_offered_products(db_mock, None, offset, limit)
#     response_json = json.loads(response.body)
#
#     offered_products_mock.assert_called_once_with(None, offset, limit)
#     self.assertEqual(response.status_code, 200)
#     self.assertEqual(response_json, business_partner_products)
