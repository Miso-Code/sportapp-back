import unittest

import faker

from app.models.schemas.schema import UserTraining
from app.utils import utils

fake = faker.Faker()


class UtilsTest(unittest.TestCase):

    def test_is_user_in_bounding_box(self):
        user = UserTraining(user_id=fake.uuid4(), latitude=1, longitude=2)
        bounding_box = utils.AdverseIncidentBoundingBox(latitude_from=0, latitude_to=2, longitude_from=1, longitude_to=3)

        response = utils.is_user_in_bounding_box(user, bounding_box)

        self.assertTrue(response)

    def test_is_user_in_bounding_box_false(self):
        user = UserTraining(user_id=fake.uuid4(), latitude=2, longitude=4)
        bounding_box = utils.AdverseIncidentBoundingBox(latitude_from=0, latitude_to=1, longitude_from=1, longitude_to=3)

        response = utils.is_user_in_bounding_box(user, bounding_box)

        self.assertFalse(response)
