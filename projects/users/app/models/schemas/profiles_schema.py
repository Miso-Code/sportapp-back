from datetime import datetime
from typing import Optional
from uuid import UUID

from pydantic import BaseModel, confloat, conint, constr, conset

from app.config.settings import Config
from app.models.schemas.schema import CreateTrainingLimitation
from app.models.users import UserIdentificationType, Gender, TrainingObjective, FoodPreference, WeekDay, UserSubscriptionType


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
    birth_date: Optional[datetime] = None


class UserPersonalProfileGet(UserPersonalProfile):
    subscription_type: UserSubscriptionType
    subscription_start_date: Optional[datetime] = None
    subscription_end_date: Optional[datetime] = None


class UserSportsProfile(BaseModel):
    favourite_sport_id: Optional[UUID] = None
    training_objective: Optional[TrainingObjective] = None
    weight: Optional[confloat(gt=0)] = None
    height: Optional[confloat(gt=0)] = None
    available_training_hours: Optional[confloat(gt=0)] = None
    available_weekdays: Optional[conset(item_type=WeekDay, min_length=1)] = []
    preferred_training_start_time: Optional[constr(pattern=Config.HOUR_REGEX)] = None


class UserSportsProfileGet(UserSportsProfile):
    training_limitations: Optional[list[dict]] = []


class UserSportsProfileUpdate(UserSportsProfile):
    training_limitations: Optional[list[CreateTrainingLimitation]] = []


class UserNutritionalProfile(BaseModel):
    food_preference: Optional[FoodPreference] = None
    nutritional_limitations: Optional[list[str]] = []
