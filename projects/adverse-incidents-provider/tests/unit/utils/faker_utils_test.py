import unittest
from faker import Faker
from app.utils.faker_utils import AdverseIncidentFakerProvider


class TestAdverseIncidentFakerProvider(unittest.TestCase):

    def setUp(self):
        self.fake = Faker()
        self.fake.add_provider(AdverseIncidentFakerProvider)

    def test_adverse_incident(self):
        incident = self.fake.adverse_incident()
        self.assertIsNotNone(incident)
        self.assertTrue(isinstance(incident, str))

    def test_all_adverse_incidents(self):
        incidents = self.fake.all_adverse_incidents()
        self.assertIsNotNone(incidents)
        self.assertTrue(isinstance(incidents, list))
        for incident in incidents:
            self.assertTrue(isinstance(incident, dict))
            self.assertIn("name", incident)
            self.assertIn("description", incident)

    def test_adverse_incidents_coverage(self):
        provider = AdverseIncidentFakerProvider(self.fake)
        incidents = provider.all_adverse_incidents()
        for incident in provider.INCIDENTS:
            self.assertIn(incident["name"], [i["name"] for i in incidents])
