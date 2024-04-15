import unittest
from unittest.mock import patch
from app.services import utils
from app.models.model import Location


class TestUtils(unittest.TestCase):
    def test_haversine(self):
        lat1, lon1 = 40.7128, 74.0060  # New York
        lat2, lon2 = 51.5074, 0.1278  # London
        result = utils._haversine(lat1, lon1, lat2, lon2)
        self.assertAlmostEqual(result, 5570.271, delta=1)  # The distance between New York and London is approximately 5570 kilometers

    def test_calculate_total_distance_coordinates(self):
        locations = [(40.7128, 74.0060), (51.5074, 0.1278)]  # New York and London
        result = utils._calculate_total_distance_coordinates(locations)
        self.assertAlmostEqual(result, 5570.271, delta=1)  # The distance between New York and London is approximately 5570 kilometers

    @patch("app.services.utils._calculate_total_distance_coordinates")
    def test_estimate_distance_with_locations(self, mock_calculate_total_distance_coordinates):
        mock_calculate_total_distance_coordinates.return_value = 5570.271
        locations = [Location(latitude=40.7128, longitude=74.0060), Location(latitude=51.5074, longitude=0.1278)]  # New York and London
        result = utils.estimate_distance(0, locations)
        self.assertAlmostEqual(result, 5570.271, delta=1)

    def test_estimate_distance_without_locations(self):
        steps = 1000
        result = utils.estimate_distance(steps, [])
        self.assertEqual(result, steps * utils.Config.AVG_STEP_LENGTH)

    def test_estimate_calories_burned(self):
        steps = 1000
        result = utils.estimate_calories_burned(steps)
        self.assertEqual(result, steps * utils.Config.AVG_CALORIES_PER_STEP)

    @patch("app.services.utils.Location")
    def test_estimate_speed_with_locations(self, mock_location):
        mock_location.speed = 10.0
        locations = [mock_location] * 5
        result = utils.estimate_speed(0, 0, locations)
        self.assertEqual(result, 10.0)

    def test_estimate_speed_without_locations(self):
        distance = 1000
        duration = 100
        result = utils.estimate_speed(distance, duration, [])
        self.assertEqual(result, distance / duration)

    def test_estimate_speed_should_return_none(self):
        result = utils.estimate_speed(0, 0, [])
        self.assertIsNone(result)
