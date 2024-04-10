from app.models.schemas.profiles_schema import UserPersonalProfile, UserSportsProfile, UserNutritionalProfile
from app.models.users import User, UserIdentificationType, FoodPreference, Gender, TrainingObjective, TrainingFrequency
from app.models.schemas.schema import UserCreate, UserAdditionalInformation, UserCredentials


def generate_random_users_create_data(faker, count):
    return [generate_random_user_create_data(faker) for _ in range(count)]


def generate_random_users(faker, count):
    return [generate_random_user(faker) for _ in range(count)]


def generate_random_users_additional_information(faker, count):
    return [generate_random_user_additional_information(faker) for _ in range(count)]


def generate_random_user_login_data(faker, token=False):
    if token:
        return UserCredentials(refresh_token=faker.uuid4())
    else:
        return UserCredentials(email=faker.email(), password=f"{faker.password()}A123!", refresh_token=None)


def generate_random_user_additional_information(faker):
    return UserAdditionalInformation(
        identification_type=faker.enum(UserIdentificationType),
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


def generate_random_user_personal_profile(faker):
    user = generate_random_user(faker)
    return UserPersonalProfile(
        email=user.email,
        first_name=user.first_name,
        last_name=user.last_name,
        identification_type=UserIdentificationType(user.identification_type),
        identification_number=user.identification_number,
        gender=Gender(user.gender),
        country_of_birth=user.country_of_birth,
        city_of_birth=user.city_of_birth,
        country_of_residence=user.country_of_residence,
        city_of_residence=user.city_of_residence,
        residence_age=user.residence_age,
        birth_date=user.birth_date,
    )


def generate_random_user_sports_profile(faker):
    user = generate_random_user(faker)
    return UserSportsProfile(
        favourite_sport_id=user.favourite_sport_id,
        training_objective=user.training_objective,
        weight=user.weight,
        height=user.height,
        available_training_hours_per_week=user.available_training_hours_per_week,
        training_frequency=TrainingFrequency(user.training_frequency),
    )


def generate_random_user_nutrition_profile(faker):
    return UserNutritionalProfile(
        food_preference=faker.enum(FoodPreference),
        nutritional_limitations=[faker.uuid4() for _ in range(faker.random_number())],
    )


def generate_random_user(faker):
    return User(
        first_name=faker.first_name(),
        last_name=faker.last_name(),
        email=faker.email(),
        hashed_password=faker.password(),
        identification_type=faker.enum(UserIdentificationType),
        identification_number=faker.random_number(),
        gender=faker.enum(Gender),
        country_of_birth=faker.country(),
        city_of_birth=faker.city(),
        country_of_residence=faker.country(),
        city_of_residence=faker.city(),
        residence_age=faker.random_number(),
        birth_date=faker.date_of_birth(minimum_age=15).isoformat(),
        favourite_sport_id=faker.uuid4(),
        training_objective=faker.enum(TrainingObjective),
        height=faker.random_int(150, 200) / 100,
        weight=faker.random_int(40, 120),
        available_training_hours_per_week=faker.random_number(),
        training_frequency=faker.enum(TrainingFrequency),
        training_years=faker.random_number(),
        food_preference=faker.enum(FoodPreference),
    )
