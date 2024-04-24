import unittest
from dataclasses import dataclass
from uuid import UUID, uuid4

from faker import Faker

from app.models.mappers.training_plan_mapper import DataClassMapper

fake = Faker()


@dataclass
class FakeClass:
    id: UUID
    description: str
    values: set[str]


class TestDataClassMapper(unittest.TestCase):
    def test_to_dict(self):
        fake_instance = FakeClass(id=uuid4(), description=fake.sentence(), values={fake.word(), fake.word(), fake.word()})

        fake_dict = DataClassMapper.to_dict(fake_instance)

        self.assertEqual(fake_dict["id"], str(fake_instance.id))
        self.assertEqual(fake_dict["description"], fake_instance.description)
        self.assertEqual(set(fake_dict["values"]), fake_instance.values)
