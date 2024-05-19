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
        latitude = fake.latitude()
        longitude = fake.longitude()

        sport_events = [DataClassMapper.to_dict(generate_random_sport_event(fake)) for _ in range(limit)]

        mock_get_sport_events.return_value = sport_events

        response = await sport_events_routes.get_sport_events(db_mock, None, offset, limit, latitude, longitude)
        response_json = json.loads(response.body)

        mock_get_sport_events.assert_called_once_with(None, offset, limit, latitude, longitude)
        self.assertEqual(response.status_code, 200)
        self.assertEqual(len(response_json), len(sport_events))
        for i in range(len(sport_events)):
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
