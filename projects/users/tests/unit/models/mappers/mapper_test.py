import unittest
import enum
from dataclasses import dataclass
from datetime import datetime
from uuid import UUID, uuid4
from faker import Faker

from app.models.mappers.user_mapper import DataClassMapper
from app.models.users import Gender
from tests.utils.users_util import generate_random_user

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
    some_date: datetime


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
            some_date=fake.date_time_this_decade(),
        )

        user_dict = DataClassMapper.to_dict(user_instance)

        # Check if all fields are properly mapped
        self.assertEqual(user_dict["id"], str(user_instance.id))
        self.assertEqual(user_dict["email"], user_instance.email)
        self.assertEqual(user_dict["first_name"], user_instance.first_name)
        self.assertEqual(user_dict["last_name"], user_instance.last_name)
        self.assertEqual(user_dict["id_type"], user_instance.id_type.value)
        self.assertEqual(user_dict["gender"], user_instance.gender.value)

    def test_to_user_personal_profile(self):
        user_instance = generate_random_user(fake)

        user_profile_dict = DataClassMapper.to_user_personal_profile(user_instance)

        self.assertEqual(user_profile_dict["email"], user_instance.email)
        self.assertEqual(user_profile_dict["first_name"], user_instance.first_name)
        self.assertEqual(user_profile_dict["last_name"], user_instance.last_name)
        self.assertEqual(user_profile_dict["identification_type"], user_instance.identification_type.value)
        self.assertEqual(user_profile_dict["identification_number"], user_instance.identification_number)
        self.assertEqual(user_profile_dict["gender"], user_instance.gender.value)
        self.assertEqual(user_profile_dict["country_of_birth"], user_instance.country_of_birth)
        self.assertEqual(user_profile_dict["city_of_birth"], user_instance.city_of_birth)
        self.assertEqual(user_profile_dict["country_of_residence"], user_instance.country_of_residence)
        self.assertEqual(user_profile_dict["city_of_residence"], user_instance.city_of_residence)
        self.assertEqual(user_profile_dict["residence_age"], user_instance.residence_age)
        self.assertEqual(user_profile_dict["birth_date"], user_instance.birth_date)

    def test_to_user_nutritional_profile(self):
        user_instance = generate_random_user(fake)

        user_profile_dict = DataClassMapper.to_user_nutritional_profile(user_instance)

        self.assertEqual(user_profile_dict["food_preference"], user_instance.food_preference.value)

    def test_to_spots_profile(self):
        user_instance = generate_random_user(fake)

        user_profile_dict = DataClassMapper.to_user_sports_profile(user_instance)

        self.assertEqual(user_profile_dict["favourite_sport_id"], user_instance.favourite_sport_id)
        self.assertEqual(user_profile_dict["training_objective"], user_instance.training_objective.value)
        self.assertEqual(user_profile_dict["weight"], user_instance.weight)
        self.assertEqual(user_profile_dict["height"], user_instance.height)
        self.assertEqual(user_profile_dict["available_training_hours"], user_instance.available_training_hours)
        self.assertEqual(user_profile_dict["available_weekdays"].sort(), user_instance.available_weekdays.split(",").sort())
        self.assertEqual(user_profile_dict["preferred_training_start_time"], user_instance.preferred_training_start_time)
        self.assertEqual(user_profile_dict["training_limitations"], user_instance.training_limitations)
