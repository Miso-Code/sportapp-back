from dataclasses import dataclass

from app.models.users import UserIdentificationType, Gender, TrainingObjective, TrainingFrequency, FoodPreference


@dataclass
class UserPersonalProfile:
    email: str
    first_name: str
    last_name: str
    identification_type: UserIdentificationType
    identification_number: str
    gender: Gender
    country_of_birth: str
    city_of_birth: str
    country_of_residence: str
    city_of_residence: str
    residence_age: int
    birth_date: str


@dataclass
class UserSportsProfile:
    favourite_sport_id: str
    training_objective: TrainingObjective
    weight: float
    height: float
    available_training_hours_per_week: int
    training_frequency: TrainingFrequency


@dataclass
class UserNutritionalProfile:
    food_preference: FoodPreference
    nutritional_limitations: list[str]
