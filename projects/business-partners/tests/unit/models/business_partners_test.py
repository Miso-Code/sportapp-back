import unittest

from app.models.business_partners import BusinessPartner
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
