import enum
import re
from datetime import datetime
from typing import Optional
from uuid import UUID

from pydantic import BaseModel, model_validator, field_validator
from app.models.users import UserIdentificationType, Gender, UserSubscriptionType, PremiumAppointmentType, FoodPreference, TrainingObjective
from app.config.settings import Config
from app.exceptions.exceptions import InvalidValueError


class SubscriptionPaymentStatus(enum.Enum):
    SUCCESS = "success"
    FAILED = "failed"


class UserCreate(BaseModel):
    first_name: str
    last_name: str
    email: str
    password: str

    @field_validator("password")
    @classmethod
    def validate_password(cls, value):
        if not re.match(Config.PASSWORD_REGEX, value):
            password_requirements = (
                "Password must be between 8 and 64 characters long and contain at least " "one digit, one lowercase letter, one uppercase letter, and one special " "character"
            )
            raise InvalidValueError(password_requirements)
        return value


class UserAdditionalInformation(BaseModel):
    identification_type: UserIdentificationType
    identification_number: str
    gender: Gender
    country_of_birth: str
    city_of_birth: str
    country_of_residence: str
    city_of_residence: str
    residence_age: int
    birth_date: datetime


class UserCredentials(BaseModel):
    refresh_token: Optional[str] = None
    email: Optional[str] = None
    password: Optional[str] = None

    @field_validator("email")
    @classmethod
    def validate_email(cls, value):
        if value is not None and not re.match(Config.EMAIL_REGEX, value):
            raise InvalidValueError("Invalid email address")
        return value

    @model_validator(mode="before")
    def validate_credentials(cls, values):
        refresh_token = values.get("refresh_token")
        email = values.get("email")
        password = values.get("password")

        if refresh_token is not None:
            if any((email, password)):
                raise InvalidValueError("Cannot provide refresh_token along with email and password")
        elif not all((email, password)):
            raise InvalidValueError("Either provide refresh_token or both email and password")

        return values


class CreateTrainingLimitation(BaseModel):
    limitation_id: Optional[UUID] = None
    name: str
    description: str


class PaymentData(BaseModel):
    card_number: str
    card_holder: str
    card_expiration_date: str
    card_cvv: str
    amount: float


class UpdateSubscriptionType(BaseModel):
    subscription_type: UserSubscriptionType
    payment_data: Optional[PaymentData] = None

    @model_validator(mode="before")
    def validate_payment_data(cls, values):
        subscription_type = values.get("subscription_type")
        payment_data = values.get("payment_data")

        if subscription_type == UserSubscriptionType.PREMIUM.value or subscription_type == UserSubscriptionType.INTERMEDIATE.value:
            if payment_data is None:
                raise InvalidValueError("Payment data is required for premium and intermediate subscriptions")

        return values


class UpdateSubscriptionTypeResponse(BaseModel):
    status: SubscriptionPaymentStatus
    message: str
    subscription_start_date: Optional[datetime] = None
    subscription_end_date: Optional[datetime] = None


class PremiumSportsmanAppointment(BaseModel):
    appointment_date: datetime
    appointment_type: PremiumAppointmentType
    appointment_location: Optional[str] = None
    trainer_id: UUID = None
    appointment_reason: str


class NutritionalPlanCreate(BaseModel):
    age: int
    gender: Gender
    training_objective: TrainingObjective
    weight: float
    height: float
    food_preference: FoodPreference
    nutritional_limitations: list[str]
