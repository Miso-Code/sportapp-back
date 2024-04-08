import unittest
from faker import Faker

from app.models.schemas.profiles_schema import UserPersonalProfile
from app.models.schemas.schema import UserCreate, UserCredentials, UserAdditionalInformation
from app.models.users import UserIdentificationType, Gender

from app.exceptions.exceptions import InvalidValueError

fake = Faker()


class TestUserProfiles(unittest.TestCase):
    def test_user_personal_profile(self):
        user_personal_profile_data = {
            "email": fake.email(),
            "first_name": fake.first_name(),
            "last_name": fake.last_name(),
            "identification_type": fake.enum(UserIdentificationType),
            "identification_number": fake.numerify(text="############"),
            "gender": fake.enum(Gender),
            "country_of_birth": fake.country(),
            "city_of_birth": fake.city(),
            "country_of_residence": fake.country(),
            "city_of_residence": fake.city(),
            "residence_age": fake.random_int(min=1, max=100),
            "birth_date": fake.date_of_birth(minimum_age=18).strftime("%Y-%m-%d"),
        }

        user_personal_profile = UserPersonalProfile(**user_personal_profile_data)
        self.assertEqual(user_personal_profile.email, user_personal_profile_data["email"])
        self.assertEqual(user_personal_profile.first_name, user_personal_profile_data["first_name"])
        self.assertEqual(user_personal_profile.last_name, user_personal_profile_data["last_name"])
        self.assertEqual(user_personal_profile.identification_type, user_personal_profile_data["identification_type"])
        self.assertEqual(user_personal_profile.identification_number, user_personal_profile_data["identification_number"])
        self.assertEqual(user_personal_profile.gender, user_personal_profile_data["gender"])
        self.assertEqual(user_personal_profile.country_of_birth, user_personal_profile_data["country_of_birth"])
        self.assertEqual(user_personal_profile.city_of_birth, user_personal_profile_data["city_of_birth"])
        self.assertEqual(user_personal_profile.country_of_residence, user_personal_profile_data["country_of_residence"])
        self.assertEqual(user_personal_profile.city_of_residence, user_personal_profile_data["city_of_residence"])
        self.assertEqual(user_personal_profile.residence_age, user_personal_profile_data["residence_age"])
        self.assertEqual(user_personal_profile.birth_date, user_personal_profile_data["birth_date"])
