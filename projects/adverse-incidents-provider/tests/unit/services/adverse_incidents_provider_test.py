import unittest
from unittest.mock import patch
from faker import Faker
from shapely import Point

from app.config.settings import Config
from app.models.schemas.schema import Coordinate
from app.services.adverse_incidents_provider import AdverseIncidentsProviderService

fake = Faker()


class TestAdverseIncidentsProvider(unittest.TestCase):

    @patch("app.utils.geo_utils.generate_random_points")
    @patch("random.randint")
    def test_randomize_adverse_incidents(self, randint_mock, generate_random_points_mock):
        mock_points = [Point(1, 1), Point(2, 2), Point(3, 3)]
        generate_random_points_mock.return_value = mock_points
        test_coordinates = [Coordinate(latitude=1, longitude=1), Coordinate(latitude=2, longitude=2), Coordinate(latitude=3, longitude=3)]
        randint_mock.return_value = 3
        incidents = AdverseIncidentsProviderService.randomize_adverse_incidents(test_coordinates)

        self.assertEqual(len(incidents), 3)

        for incident in incidents:
            self.assertIn("description", incident)
            self.assertIn("bounding_box", incident)
            self.assertIn("latitude_from", incident["bounding_box"])
            self.assertIn("longitude_from", incident["bounding_box"])
            self.assertIn("latitude_to", incident["bounding_box"])
            self.assertIn("longitude_to", incident["bounding_box"])
            self.assertIsInstance(incident["description"], str)
            self.assertIsInstance(incident["bounding_box"]["latitude_from"], float)
            self.assertIsInstance(incident["bounding_box"]["longitude_from"], float)
            self.assertIsInstance(incident["bounding_box"]["latitude_to"], float)
            self.assertIsInstance(incident["bounding_box"]["longitude_to"], float)
            self.assertEqual(incident["bounding_box"]["latitude_from"], mock_points[incidents.index(incident)].y - Config.ADVERSE_INCIDENTS_AFFECTED_RANGE)
            self.assertEqual(incident["bounding_box"]["longitude_from"], mock_points[incidents.index(incident)].x - Config.ADVERSE_INCIDENTS_AFFECTED_RANGE)
            self.assertEqual(incident["bounding_box"]["latitude_to"], mock_points[incidents.index(incident)].y + Config.ADVERSE_INCIDENTS_AFFECTED_RANGE)
            self.assertEqual(incident["bounding_box"]["longitude_to"], mock_points[incidents.index(incident)].x + Config.ADVERSE_INCIDENTS_AFFECTED_RANGE)
