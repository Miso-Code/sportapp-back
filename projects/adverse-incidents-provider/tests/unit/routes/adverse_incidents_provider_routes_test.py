import json
import unittest

from unittest.mock import patch

from faker import Faker

from app.models.schemas.schema import Coordinate

fake = Faker()


class TestSportEventsRoutes(unittest.IsolatedAsyncioTestCase):

    @patch("app.services.adverse_incidents_provider.AdverseIncidentsProviderService.randomize_adverse_incidents")
    async def test_generate_incidents(self, mock_randomize_adverse_incidents):
        from app.routes.adverse_incidents_provider_routes import generate_incidents

        mock_response = [
            {"description": "Test incident", "bounding_box": {"latitude_from": 1, "longitude_from": 1, "latitude_to": 2, "longitude_to": 2}},
            {"description": "Test incident 2", "bounding_box": {"latitude_from": 3, "longitude_from": 3, "latitude_to": 4, "longitude_to": 4}},
        ]

        mock_randomize_adverse_incidents.return_value = mock_response

        test_coordinates = [Coordinate(latitude=1, longitude=1), Coordinate(latitude=2, longitude=2), Coordinate(latitude=3, longitude=3)]

        response = await generate_incidents(test_coordinates)
        response_json = json.loads(response.body)

        self.assertEqual(response.status_code, 200)
        self.assertEqual(response_json, mock_response)
