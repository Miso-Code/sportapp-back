import unittest
from uuid import UUID

from faker import Faker

from app.models.schemas.profiles_schema import UserPersonalProfile, UserSportsProfile, UserNutritionalProfile
from app.models.users import UserIdentificationType, Gender, TrainingObjective, FoodPreference
from tests.utils.users_util import week_days

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
            "birth_date": fake.date_time_this_decade(),
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

    def test_user_sports_profile(self):
        user_sports_profile_data = {
            "favourite_sport_id": fake.uuid4(),
            "training_objective": fake.enum(TrainingObjective).value,
            "weight": fake.random_int(min=1, max=100),
            "height": fake.random_int(min=1, max=100),
            "available_training_hours": fake.random_int(min=1, max=100),
            "available_weekdays": list(set(fake.random_choices(week_days, length=fake.random_number(1, 7)))),
            "preferred_training_start_time": fake.time("%I:%M %p"),
        }

        user_sports_profile = UserSportsProfile(**user_sports_profile_data)

        self.assertEqual(user_sports_profile.favourite_sport_id, UUID(user_sports_profile_data["favourite_sport_id"]))
        self.assertEqual(user_sports_profile.training_objective.value, user_sports_profile_data["training_objective"])
        self.assertEqual(user_sports_profile.weight, user_sports_profile_data["weight"])
        self.assertEqual(user_sports_profile.height, user_sports_profile_data["height"])
        self.assertEqual(user_sports_profile.available_training_hours, user_sports_profile_data["available_training_hours"])
        self.assertEqual(user_sports_profile.available_weekdays, set(user_sports_profile_data["available_weekdays"]))
        self.assertEqual(user_sports_profile.preferred_training_start_time, user_sports_profile_data["preferred_training_start_time"])

    def test_user_nutritional_profile(self):
        user_nutritional_profile_data = {
            "food_preference": fake.enum(FoodPreference).value,
            "nutritional_limitations": [fake.word() for _ in range(fake.random_int(min=1, max=5))],
        }

        user_nutritional_profile = UserNutritionalProfile(**user_nutritional_profile_data)

        self.assertEqual(user_nutritional_profile.food_preference.value, user_nutritional_profile_data["food_preference"])
        self.assertEqual(user_nutritional_profile.nutritional_limitations, user_nutritional_profile_data["nutritional_limitations"])
