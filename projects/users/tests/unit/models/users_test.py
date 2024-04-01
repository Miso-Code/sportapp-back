import unittest

import faker
from app.models.users import User, UserIdentificationType, FoodPreference, Gender, UserSubscriptionType


class TestUser(unittest.TestCase):
    fake = faker.Faker("en_US")

    def test_user_creation(self):
        user_id = self.fake.uuid4()
        first_name = self.fake.first_name()
        last_name = self.fake.last_name()
        email = self.fake.email()
        hashed_password = self.fake.password()
        identification_type = self.fake.enum(UserIdentificationType)
        identification_number = self.fake.random_number()
        gender = self.fake.enum(Gender)
        country_of_birth = self.fake.country()
        city_of_birth = self.fake.city()
        country_of_residence = self.fake.country()
        city_of_residence = self.fake.city()
        residence_age = self.fake.random_number()
        birth_date = self.fake.date_of_birth(minimum_age=15)
        weight = self.fake.pyfloat(left_digits=2, right_digits=2, positive=True)
        height = self.fake.pyfloat(left_digits=3, right_digits=2, positive=True)
        training_years = self.fake.random_number()
        training_hours_per_week = self.fake.random_number()
        available_training_hours_per_week = self.fake.random_number()
        food_preference = self.fake.enum(FoodPreference)
        subscription_type = self.fake.enum(UserSubscriptionType)

        user = User(
            user_id=user_id,
            first_name=first_name,
            last_name=last_name,
            email=email,
            hashed_password=hashed_password,
            identification_type=identification_type,
            identification_number=identification_number,
            gender=gender,
            country_of_birth=country_of_birth,
            city_of_birth=city_of_birth,
            country_of_residence=country_of_residence,
            city_of_residence=city_of_residence,
            residence_age=residence_age,
            birth_date=birth_date,
            weight=weight,
            height=height,
            training_years=training_years,
            training_hours_per_week=training_hours_per_week,
            available_training_hours_per_week=available_training_hours_per_week,
            food_preference=food_preference,
            subscription_type=subscription_type,
        )

        self.assertEqual(user.user_id, user_id)
        self.assertEqual(user.first_name, first_name)
        self.assertEqual(user.last_name, last_name)
        self.assertEqual(user.email, email)
        self.assertEqual(user.hashed_password, hashed_password)
        self.assertEqual(user.identification_type, identification_type)
        self.assertEqual(user.identification_number, identification_number)
        self.assertEqual(user.gender, gender)
        self.assertEqual(user.country_of_birth, country_of_birth)
        self.assertEqual(user.city_of_birth, city_of_birth)
        self.assertEqual(user.country_of_residence, country_of_residence)
        self.assertEqual(user.city_of_residence, city_of_residence)
        self.assertEqual(user.residence_age, residence_age)
        self.assertEqual(user.birth_date, birth_date)
        self.assertEqual(user.weight, weight)
        self.assertEqual(user.height, height)
        self.assertEqual(user.training_years, training_years)
        self.assertEqual(user.training_hours_per_week, training_hours_per_week)
        self.assertEqual(user.available_training_hours_per_week, available_training_hours_per_week)
        self.assertEqual(user.food_preference, food_preference)
        self.assertEqual(user.subscription_type, subscription_type)
