import re
from typing import Optional
from uuid import UUID

from pydantic import BaseModel, model_validator, field_validator
from app.models.users import UserIdentificationType, Gender
from app.config.settings import Config
from app.exceptions.exceptions import InvalidValueError


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
    birth_date: str

    @field_validator("birth_date")
    @classmethod
    def validate_birth_date(cls, value):
        if not re.match(Config.BIRTH_DATE_REGEX, value):
            raise InvalidValueError("Birth date must be in the format YYYY-MM-DD")
        return value


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


class BusinessPartnerCreate(BaseModel):
    business_partner_name: str
    email: str
    password: str
