import unittest
import enum
from dataclasses import dataclass
from uuid import UUID, uuid4
from faker import Faker

from app.models.mappers.user_mapper import DataClassMapper

fake = Faker()


class FakeEnum(enum.Enum):
    TEST1 = "TEST1"
    TEST2 = "TEST2"


@dataclass
class FakeClass:
    id: UUID
    field1: str
    field2: str
    field3: FakeEnum


class TestDataClassMapper(unittest.TestCase):
    def test_to_dict(self):
        fake_class = FakeClass(id=uuid4(), field1=fake.word(), field2=fake.word(), field3=fake.enum(FakeEnum))
        fake_class_dict = DataClassMapper.to_dict(fake_class)
        self.assertEqual(fake_class_dict["id"], str(fake_class.id))
        self.assertEqual(fake_class_dict["field1"], fake_class.field1)
        self.assertEqual(fake_class_dict["field2"], fake_class.field2)
        self.assertEqual(fake_class_dict["field3"], fake_class.field3.value)
