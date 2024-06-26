import unittest
from app.models.users import User, UserIdentificationType, Gender, TrainingObjective
from faker import Faker

fake = Faker()


class TestUser(unittest.TestCase):
    def test_user_creation(self):
        user_data = {
            "user_id": fake.uuid4(),
            "first_name": fake.first_name(),
            "last_name": fake.last_name(),
            "email": fake.email(),
            "hashed_password": fake.password(),
            "identification_type": fake.enum(UserIdentificationType),
            "identification_number": fake.random_int(min=1000000, max=9999999999),
            "gender": fake.enum(Gender),
            "country_of_birth": fake.country(),
            "city_of_birth": fake.city(),
            "country_of_residence": fake.country(),
            "city_of_residence": fake.city(),
            "residence_age": fake.random_int(min=1, max=100),
            "birth_date": fake.date_of_birth(minimum_age=18, maximum_age=100),
            "favourite_sport_id": fake.uuid4(),
            "training_objective": fake.enum(TrainingObjective),
            "weight": fake.random_int(min=1, max=200),
            "height": fake.random_int(min=1, max=200),
            "available_training_hours": fake.random_int(min=1, max=50),
            "training_years": fake.random_int(min=1, max=50),
            "available_weekdays": fake.words(nb=3),
            "preferred_training_start_time": fake.time("%H:%M:%S"),
        }

        user = User(**user_data)

        self.assertEqual(user.user_id, user_data["user_id"])
        self.assertEqual(user.first_name, user_data["first_name"])
        self.assertEqual(user.last_name, user_data["last_name"])
        self.assertEqual(user.email, user_data["email"])
        self.assertEqual(user.hashed_password, user_data["hashed_password"])
        self.assertEqual(user.identification_type, user_data["identification_type"])
        self.assertEqual(user.identification_number, user_data["identification_number"])
        self.assertEqual(user.gender, user_data["gender"])
        self.assertEqual(user.country_of_birth, user_data["country_of_birth"])
        self.assertEqual(user.city_of_birth, user_data["city_of_birth"])
        self.assertEqual(user.country_of_residence, user_data["country_of_residence"])
        self.assertEqual(user.city_of_residence, user_data["city_of_residence"])
        self.assertEqual(user.residence_age, user_data["residence_age"])
        self.assertEqual(user.birth_date, user_data["birth_date"])
        self.assertEqual(user.favourite_sport_id, user_data["favourite_sport_id"])
        self.assertEqual(user.training_objective, user_data["training_objective"])
        self.assertEqual(user.weight, user_data["weight"])
        self.assertEqual(user.height, user_data["height"])
        self.assertEqual(user.available_training_hours, user_data["available_training_hours"])
        self.assertEqual(user.training_years, user_data["training_years"])
        self.assertEqual(user.available_weekdays, user_data["available_weekdays"])
        self.assertEqual(user.preferred_training_start_time, user_data["preferred_training_start_time"])
