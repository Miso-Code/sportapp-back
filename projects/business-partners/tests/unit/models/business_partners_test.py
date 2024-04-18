import unittest

from app.models.business_partners import BusinessPartner, BusinessPartnerProduct, ProductCategory, PaymentFrequency, PaymentType
from faker import Faker

fake = Faker()


class TestBusinessPartner(unittest.TestCase):
    def test_business_partner_creation(self):
        business_partner_data = {
            "business_partner_id": fake.uuid4(),
            "business_partner_name": fake.company(),
            "email": fake.email(),
            "hashed_password": fake.password(),
        }

        business_partner = BusinessPartner(**business_partner_data)

        self.assertEqual(business_partner.business_partner_id, business_partner_data["business_partner_id"])
        self.assertEqual(business_partner.business_partner_name, business_partner_data["business_partner_name"])
        self.assertEqual(business_partner.email, business_partner_data["email"])
        self.assertEqual(business_partner.hashed_password, business_partner_data["hashed_password"])

    def test_business_partner_product_create(self):
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
            "description": fake.text(),
        }

        business_partner_product = BusinessPartnerProduct(**product_data)

        self.assertEqual(business_partner_product.product_id, product_data["product_id"])
        self.assertEqual(business_partner_product.business_partner_id, product_data["business_partner_id"])
        self.assertEqual(business_partner_product.category, product_data["category"])
        self.assertEqual(business_partner_product.name, product_data["name"])
        self.assertEqual(business_partner_product.url, product_data["url"])
        self.assertEqual(business_partner_product.price, product_data["price"])
        self.assertEqual(business_partner_product.payment_type, product_data["payment_type"])
        self.assertEqual(business_partner_product.payment_frequency, product_data["payment_frequency"])
        self.assertEqual(business_partner_product.image_url, product_data["image_url"])
        self.assertEqual(business_partner_product.description, product_data["description"])
