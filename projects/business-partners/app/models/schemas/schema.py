from typing import Optional

from pydantic import BaseModel, model_validator
from app.exceptions.exceptions import InvalidValueError


class BusinessPartnerCredentials(BaseModel):
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
                raise InvalidValueError("Cannot provide refresh_token along with email and password")
        elif not all((email, password)):
            raise InvalidValueError("Either provide refresh_token or both email and password")

        return values


class BusinessPartnerCreate(BaseModel):
    business_partner_name: str
    email: str
    password: str
