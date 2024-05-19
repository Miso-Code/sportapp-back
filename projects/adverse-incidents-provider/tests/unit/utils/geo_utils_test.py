import unittest
from unittest.mock import patch, MagicMock
from shapely.geometry import Point
from app.utils.geo_utils import generate_random_points

from app.models.schemas.schema import Coordinate


class TestRandomPointGenerator(unittest.TestCase):

    @patch("app.config.settings.Config")
    def test_generate_random_points_without_boundary_coords(self, mock_config):
        mock_config.CALI_BOUNDARY_CODES = [Coordinate(latitude=0, longitude=0), Coordinate(latitude=1, longitude=1)]

        points = generate_random_points(num_points=5, boundary_coords=None)
        self.assertEqual(len(points), 5)
        for point in points:
            self.assertIsInstance(point, Point)

    @patch("app.config.settings.Config")
    def test_generate_random_points_with_boundary_coords(self, mock_config):
        boundary_coords = [Coordinate(latitude=0, longitude=0), Coordinate(latitude=2, longitude=2), Coordinate(latitude=0, longitude=2), Coordinate(latitude=2, longitude=0)]

        points = generate_random_points(num_points=5, boundary_coords=boundary_coords)
        self.assertEqual(len(points), 5)
        mock_config.assert_not_called()
        for point in points:
            self.assertIsInstance(point, Point)
