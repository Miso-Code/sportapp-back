import unittest
from app.models.users import User, UserIdentificationType, FoodPreference, Gender, UserSubscriptionType
from faker import Faker

fake = Faker()


class TestUser(unittest.TestCase):
    def test_user_creation(self):
        user_id = fake.uuid4()
        first_name = fake.first_name()
        last_name = fake.last_name()
        email = fake.email()
        hashed_password = fake.password()
        identification_type = UserIdentificationType(fake.random_element(elements=[e.value for e in UserIdentificationType]))
        identification_number = fake.random_number()
        gender = Gender(fake.random_element(elements=[e.value for e in Gender]))
        country_of_birth = fake.country()
        city_of_birth = fake.city()
        country_of_residence = fake.country()
        city_of_residence = fake.city()
        residence_age = fake.random_number()
        birth_date = fake.date_of_birth(minimum_age=15)
        weight = fake.pyfloat(left_digits=2, right_digits=2, positive=True)
        height = fake.pyfloat(left_digits=3, right_digits=2, positive=True)
        training_years = fake.random_number()
        training_hours_per_week = fake.random_number()
        available_training_hours_per_week = fake.random_number()
        food_preference = FoodPreference(fake.random_element(elements=[e.value for e in FoodPreference]))
        subscription_type = UserSubscriptionType(fake.random_element(elements=[e.value for e in UserSubscriptionType]))

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
