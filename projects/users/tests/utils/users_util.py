from uuid import UUID

from app.models.schemas.profiles_schema import UserPersonalProfile, UserSportsProfile, UserNutritionalProfile, UserSportsProfileUpdate
from app.models.users import (
    User,
    UserIdentificationType,
    FoodPreference,
    Gender,
    TrainingObjective,
    NutritionalLimitation,
    WeekDay,
    UserSubscriptionType,
    Trainer,
    PremiumAppointmentType,
    UserSportsmanAppointment,
)
from app.models.schemas.schema import (
    UserCreate,
    UserAdditionalInformation,
    UserCredentials,
    CreateTrainingLimitation,
    UpdateSubscriptionType,
    PaymentData,
    PremiumSportsmanAppointment,
)


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
        birth_date=faker.date_time_this_decade(),
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
        available_training_hours=user.available_training_hours,
        available_week_days=set(user.available_weekdays.split(",")),
        preferred_training_start_time=user.preferred_training_start_time,
    )


def generate_random_user_sport_profile_update(faker):
    return UserSportsProfileUpdate(
        favourite_sport_id=faker.uuid4(),
        training_objective=faker.enum(TrainingObjective),
        weight=faker.random_int(40, 120),
        height=faker.random_int(150, 200) / 100,
        available_training_hours=faker.random_number(1, 20),
        available_week_days=faker.random_choices(week_days, unique=True, length=faker.random_number(1, 7)),
        preferred_training_start_time=faker.time(),
        training_limitations=[CreateTrainingLimitation(name=faker.word(), description=faker.sentence()) for _ in range(faker.random_number(1, 5))],
    )


def generate_random_user_nutritional_profile(faker):
    return UserNutritionalProfile(
        food_preference=faker.enum(FoodPreference),
        nutritional_limitations=[faker.uuid4() for _ in range(2)],
    )


week_days: list[WeekDay] = ["monday", "tuesday", "wednesday", "thursday", "friday", "saturday", "sunday"]


def generate_random_user(faker):
    return User(
        first_name=faker.first_name(),
        last_name=faker.last_name(),
        email=faker.email(),
        hashed_password=faker.password(),
        identification_type=faker.enum(UserIdentificationType),
        identification_number=faker.numerify(text="############"),
        gender=faker.enum(Gender),
        country_of_birth=faker.country(),
        city_of_birth=faker.city(),
        country_of_residence=faker.country(),
        city_of_residence=faker.city(),
        residence_age=faker.random_number(),
        birth_date=faker.date_time_this_decade(),
        favourite_sport_id=faker.uuid4(),
        training_objective=faker.enum(TrainingObjective),
        available_weekdays=",".join(list(set(faker.random_choices(week_days, length=faker.random_number(1, 7))))),
        available_training_hours=faker.random_number(1, 20),
        preferred_training_start_time=faker.time("%I:%M %p"),
        height=faker.random_int(150, 200) / 100,
        weight=faker.random_int(40, 120),
        training_years=faker.random_number(1, 20),
        food_preference=faker.enum(FoodPreference),
        subscription_type=faker.enum(UserSubscriptionType),
        subscription_start_date=faker.date_time_this_decade(),
        subscription_end_date=faker.date_time_this_decade(),
    )


def generate_random_user_nutritional_limitation(faker):
    return NutritionalLimitation(
        limitation_id=UUID(faker.uuid4()),
        name=faker.word(),
        description=faker.sentence(),
    )


def generate_random_update_user_plan(faker):
    return UpdateSubscriptionType(
        subscription_type=faker.enum(UserSubscriptionType),
        payment_data=PaymentData(
            card_number=faker.credit_card_number(),
            card_holder=faker.name(),
            card_expiration_date=faker.credit_card_expire(),
            card_cvv=faker.credit_card_security_code(),
            amount=faker.random_number(1, 1000),
        ),
    )


def generate_random_trainer(faker):
    return Trainer(
        trainer_id=faker.uuid4(),
        first_name=faker.first_name(),
        last_name=faker.last_name(),
    )


def generate_random_appointment_data(faker, trainer_id, address: bool = False):
    address = faker.address() if address else None
    return PremiumSportsmanAppointment(
        appointment_date=faker.date_time_this_year(),
        appointment_type=faker.enum(PremiumAppointmentType),
        appointment_location=address,
        trainer_id=trainer_id,
        appointment_reason=faker.sentence(),
    )


def generate_random_appointment(faker):
    return UserSportsmanAppointment(
        user_id=faker.uuid4(),
        appointment_date=faker.date_time_this_year(),
        appointment_type=faker.enum(PremiumAppointmentType),
        appointment_location=faker.address(),
        trainer_id=faker.uuid4(),
        appointment_reason=faker.sentence(),
    )
