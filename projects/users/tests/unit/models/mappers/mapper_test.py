import unittest
import enum
from dataclasses import dataclass
from uuid import UUID, uuid4
from faker import Faker

from app.models.mappers.mapper import DataClassMapper

fake = Faker()


class UserIdentificationType(enum.Enum):
    CEDULA_CIUDADANIA = "CC"
    CEDULA_EXTRANJERIA = "CE"
    PASAPORTE = "PA"
    TARJETA_IDENTIDAD = "TI"


@dataclass
class FakeDataClass:
    id: UUID
    name: str
    type: UserIdentificationType
    age: int


class TestDataClassMapper(unittest.TestCase):
    def setUp(self):
        self.mapper = DataClassMapper(FakeDataClass)

    def test_to_dict(self):
        # Generate random data using Faker
        instance = FakeDataClass(id=uuid4(), name=fake.name(), type=UserIdentificationType.CEDULA_CIUDADANIA, age=fake.random_int(min=18, max=100))

        # Map dataclass instance to dictionary
        result_dict = self.mapper.to_dict(instance)

        # Check if all fields are properly mapped
        self.assertEqual(result_dict["id"], str(instance.id))
        self.assertEqual(result_dict["name"], instance.name)
        self.assertEqual(result_dict["type"], instance.type.value)
        self.assertEqual(result_dict["age"], instance.age)
