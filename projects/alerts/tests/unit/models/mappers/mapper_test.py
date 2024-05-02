import unittest
from dataclasses import dataclass
from uuid import UUID, uuid4
from faker import Faker

from app.models.mappers.data_mapper import DataClassMapper

fake = Faker()


@dataclass
class FakeClass:
    id: UUID
    field1: str
    field2: str


class TestDataClassMapper(unittest.TestCase):
    def test_to_dict(self):
        fake_class = FakeClass(id=uuid4(), field1=fake.word(), field2=fake.word())
        fake_class_dict = DataClassMapper.to_dict(fake_class)
        self.assertEqual(fake_class_dict["id"], str(fake_class.id))
        self.assertEqual(fake_class_dict["field1"], fake_class.field1)
        self.assertEqual(fake_class_dict["field2"], fake_class.field2)
