import unittest
import enum
from dataclasses import dataclass
from uuid import UUID, uuid4
from faker import Faker

from app.models.mappers.user_mapper import DataClassMapper
from app.models.users import Gender

fake = Faker()


class UserIdentificationType(enum.Enum):
    CEDULA_CIUDADANIA = "CC"
    CEDULA_EXTRANJERIA = "CE"
    PASAPORTE = "PA"
    TARJETA_IDENTIDAD = "TI"


@dataclass
class FakeUserClass:
    id: UUID
    email: str
    first_name: str
    last_name: str
    id_type: UserIdentificationType
    gender: Gender


@dataclass
class FakeUserProfileClass:
    id_type: UserIdentificationType
    gender: Gender


class TestDataClassMapper(unittest.TestCase):
    def test_to_dict(self):
        # Generate random data using Faker
        user_instance = FakeUserClass(
            id=uuid4(),
            email=fake.email(),
            first_name=fake.first_name(),
            last_name=fake.last_name(),
            id_type=fake.random_element(elements=UserIdentificationType),
            gender=fake.random_element(elements=Gender),
        )

        user_dict = DataClassMapper.to_dict(user_instance)

        # Check if all fields are properly mapped
        self.assertEqual(user_dict["id"], str(user_instance.id))
        self.assertEqual(user_dict["email"], user_instance.email)
        self.assertEqual(user_dict["first_name"], user_instance.first_name)
        self.assertEqual(user_dict["last_name"], user_instance.last_name)
        self.assertEqual(user_dict["id_type"], user_instance.id_type.value)
        self.assertEqual(user_dict["gender"], user_instance.gender.value)

    def test_to_users_profile_dict(self):
        # Generate random data using Faker
        user_instance = FakeUserClass(
            id=uuid4(),
            email=fake.email(),
            first_name=fake.first_name(),
            last_name=fake.last_name(),
            id_type=fake.random_element(elements=UserIdentificationType),
            gender=fake.random_element(elements=Gender),
        )

        # Map dataclass instance to dictionary
        user_profile_dict = DataClassMapper.to_user_subclass_dict(user_instance, FakeUserProfileClass)

        self.assertEqual(user_profile_dict["id_type"], user_instance.id_type.value)
        self.assertEqual(user_profile_dict["gender"], user_instance.gender.value)
        self.assertNotIn("email", user_profile_dict)
        self.assertNotIn("first_name", user_profile_dict)
        self.assertNotIn("last_name", user_profile_dict)
        self.assertNotIn("id", user_profile_dict)
