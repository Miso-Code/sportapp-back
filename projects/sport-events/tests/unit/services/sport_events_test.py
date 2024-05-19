import unittest
from unittest.mock import MagicMock
from faker import Faker
from sqlalchemy.orm import Session
from app.exceptions.exceptions import NotFoundError
from app.services.sport_events import SportEventsService
from tests.utils.sport_events_util import generate_random_sport_event_data, generate_random_sport_event

fake = Faker()


class TestSportEventsService(unittest.TestCase):
    def setUp(self):
        self.mock_db = MagicMock(spec=Session)
        self.jwt_manager_mock = MagicMock()
        self.sport_events_service = SportEventsService(db=self.mock_db)
        self.sport_events_service.jwt_manager = self.jwt_manager_mock

    def test_create_sport_event(self):
        sport_event_data = generate_random_sport_event_data(fake)

        response = self.sport_events_service.create_sport_event(sport_event_data)

        self.assertEqual(response["title"], sport_event_data.title)
        self.assertEqual(response["sport_id"], str(sport_event_data.sport_id))
        self.assertEqual(response["start_date"], sport_event_data.start_date.isoformat())
        self.assertEqual(response["end_date"], sport_event_data.end_date.isoformat())
        self.assertEqual(response["location_latitude"], sport_event_data.location_latitude)
        self.assertEqual(response["location_longitude"], sport_event_data.location_longitude)
        self.assertEqual(response["description"], sport_event_data.description)

    def test_get_sport_events_no_search(self):
        mocked_events = [generate_random_sport_event(fake) for _ in range(3)]
        self.mock_db.query.return_value.filter.return_value.order_by.return_value.offset.return_value.limit.return_value.all.return_value = mocked_events

        response = self.sport_events_service.get_sport_events(None, 0, 3)

        self.assertEqual(len(response), len(mocked_events))
        for event in response:
            print(event)
            self.assertIn("title", event)
            self.assertIn("sport_id", event)
            self.assertIn("event_id", event)
            self.assertIn("description", event)
            self.assertIn("start_date", event)
            self.assertIn("end_date", event)
            self.assertIn("location_latitude", event)
            self.assertIn("location_longitude", event)
            self.assertIn("capacity", event)

    def test_get_sport_events_with_search(self):
        search = fake.word()
        mocked_events = [generate_random_sport_event(fake) for _ in range(3)]
        self.mock_db.query.return_value.filter.return_value.order_by.return_value.offset.return_value.limit.return_value.all.return_value = mocked_events

        response = self.sport_events_service.get_sport_events(search, 0, 3)

        self.assertEqual(len(response), len(mocked_events))
        for event in response:
            self.assertIn("title", event)
            self.assertIn("sport_id", event)
            self.assertIn("event_id", event)
            self.assertIn("description", event)
            self.assertIn("start_date", event)
            self.assertIn("end_date", event)
            self.assertIn("location_latitude", event)
            self.assertIn("location_longitude", event)
            self.assertIn("capacity", event)

    def test_get_sport_events_with_latitude_and_longitude(self):
        mocked_events = [generate_random_sport_event(fake) for _ in range(3)]
        self.mock_db.query.return_value.filter.return_value.order_by.return_value.offset.return_value.limit.return_value.all.return_value = mocked_events

        response = self.sport_events_service.get_sport_events(None, 0, 3, 0.0, 0.0)

        self.assertEqual(len(response), len(mocked_events))
        for event in response:
            self.assertIn("title", event)
            self.assertIn("sport_id", event)
            self.assertIn("event_id", event)
            self.assertIn("description", event)
            self.assertIn("start_date", event)
            self.assertIn("end_date", event)
            self.assertIn("location_latitude", event)
            self.assertIn("location_longitude", event)
            self.assertIn("capacity", event)

    def test_get_sport_event(self):
        sport_event = generate_random_sport_event(fake)
        self.mock_db.query.return_value.filter.return_value.first.return_value = sport_event

        response = self.sport_events_service.get_sport_event(sport_event.event_id)

        self.assertEqual(response["title"], sport_event.title)
        self.assertEqual(response["sport_id"], str(sport_event.sport_id))
        self.assertEqual(response["event_id"], str(sport_event.event_id))
        self.assertEqual(response["description"], sport_event.description)
        self.assertEqual(response["start_date"], sport_event.start_date.isoformat())
        self.assertEqual(response["end_date"], sport_event.end_date.isoformat())
        self.assertEqual(response["location_latitude"], sport_event.location_latitude)
        self.assertEqual(response["location_longitude"], sport_event.location_longitude)
        self.assertEqual(response["capacity"], sport_event.capacity)

    def test_get_sport_event_not_found(self):
        sport_event_id = fake.uuid4()
        self.mock_db.query.return_value.filter.return_value.first.return_value = None

        with self.assertRaises(NotFoundError) as context:
            self.sport_events_service.get_sport_event(sport_event_id)

        self.assertEqual(str(context.exception), "Sport event not found")
