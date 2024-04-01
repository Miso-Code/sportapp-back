from app.models.users import User, UserIdentificationType, FoodPreference, Gender, UserSubscriptionType


def generate_random_users(count, faker):
    return [generate_random_user(faker) for _ in range(count)]


def generate_random_user(faker):
    return User(
        user_id=faker.fake.uuid4(),
        first_name=faker.fake.first_name(),
        last_name=faker.fake.last_name(),
        email=faker.fake.email(),
        hashed_password=faker.fake.password(),
        identification_type=faker.fake.random_element(elements=UserIdentificationType),
        identification_number=faker.fake.random_number(),
        gender=faker.fake.random_element(elements=Gender),
        country_of_birth=faker.fake.country(),
        city_of_birth=faker.fake.city(),
        country_of_residence=faker.fake.country(),
        city_of_residence=faker.fake.city(),
        residence_age=faker.fake.random_number(),
        birth_date=faker.fake.date_of_birth(minimum_age=15).isoformat(),
        weight=faker.fake.pyfloat(left_digits=2, right_digits=2, positive=True),
        height=faker.fake.pyfloat(left_digits=3, right_digits=2, positive=True),
        training_years=faker.fake.random_number(),
        training_hours_per_week=faker.fake.random_number(),
        available_training_hours_per_week=faker.fake.random_number(),
        food_preference=faker.fake.random_element(elements=FoodPreference),
        subscription_type=faker.fake.random_element(elements=UserSubscriptionType),
    )
