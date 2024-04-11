from typing import Optional
from uuid import UUID

from pydantic import BaseModel, confloat, conint

from app.models.users import UserIdentificationType, Gender, TrainingObjective, TrainingFrequency, FoodPreference


class UserPersonalProfile(BaseModel):
    email: Optional[str] = None
    first_name: Optional[str] = None
    last_name: Optional[str] = None
    identification_type: Optional[UserIdentificationType] = None
    identification_number: Optional[str] = None
    gender: Optional[Gender] = None
    country_of_birth: Optional[str] = None
    city_of_birth: Optional[str] = None
    country_of_residence: Optional[str] = None
    city_of_residence: Optional[str] = None
    residence_age: Optional[conint(ge=0)] = None
    birth_date: Optional[str] = None


class UserSportsProfile(BaseModel):
    favourite_sport_id: Optional[UUID]
    training_objective: Optional[TrainingObjective]
    weight: Optional[confloat(gt=0)]
    height: Optional[confloat(gt=0)]
    available_training_hours_per_week: Optional[confloat(gt=0)]
    training_frequency: Optional[TrainingFrequency]


class UserNutritionalProfile(BaseModel):
    food_preference: Optional[FoodPreference]
    nutritional_limitations: Optional[list[str]]
