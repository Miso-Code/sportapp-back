import re
from typing import Optional

from pydantic import BaseModel, model_validator, field_validator

PASSWORD_REGEX = r"((?=.*\d)(?=.*[a-z])(?=.*[A-Z])(?=.*[\W]).{8,64})"


class UserCreate(BaseModel):
    first_name: str
    last_name: str
    email: str
    password: str

    @field_validator("password")
    @classmethod
    def validate_password(cls, value):
        if not re.match(PASSWORD_REGEX, value):
            raise ValueError(
                "Password must be between 8 and 64 characters long and contain at least one digit, one lowercase " "letter, one uppercase letter, and one special character",
            )
        return value


class UserCredentials(BaseModel):
    refresh_token: Optional[str] = None
    email: Optional[str] = None
    password: Optional[str] = None

    @model_validator(mode="before")
    def validate_credentials(cls, values):
        refresh_token = values.get("refresh_token")
        email = values.get("email")
        password = values.get("password")

        if refresh_token is not None:
            if any((email, password)):
                raise ValueError("Cannot provide refresh_token along with email and password")
        elif all((email, password)):
            return values
        else:
            raise ValueError("Either provide refresh_token or both email and password")

        return values
