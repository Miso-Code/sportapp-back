from app.models.users import User, UserIdentificationType, FoodPreference, Gender, UserSubscriptionType
from app.models.schemas.schema import UserCreate, UserAdditionalInformation


def generate_random_users_create_data(faker, count):
    return [generate_random_user_create_data(faker) for _ in range(count)]


def generate_random_users(faker, count):
    return [generate_random_user(faker) for _ in range(count)]


def generate_random_users_additional_information(faker, count):
    return [generate_random_user_additional_information(faker) for _ in range(count)]


def generate_random_user_additional_information(faker):
    return UserAdditionalInformation(
        identification_type=faker.enum(UserIdentificationType).value,
        identification_number=faker.numerify(text="############"),
        gender=faker.enum(Gender),
        country_of_birth=faker.country(),
        city_of_birth=faker.city(),
        country_of_residence=faker.country(),
        city_of_residence=faker.city(),
        residence_age=faker.random_number(),
        birth_date=faker.date_of_birth(minimum_age=18).strftime("%Y-%m-%d"),
    )


def generate_random_user_create_data(faker):
    return UserCreate(first_name=faker.first_name(), last_name=faker.last_name(), email=faker.email(), password=f"{faker.password()}A123!")


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
