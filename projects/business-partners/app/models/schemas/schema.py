from typing import Optional

from pydantic import BaseModel, model_validator
from app.exceptions.exceptions import InvalidValueError
from app.models.business_partners import ProductCategory, PaymentType, PaymentFrequency


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


class CreateBusinessPartnerProduct(BaseModel):
    category: ProductCategory
    name: str
    url: str
    price: float
    payment_type: PaymentType
    payment_frequency: PaymentFrequency
    image_url: Optional[str] = None
    image_base64: Optional[str] = None
    description: str
    active: Optional[bool] = True

    @model_validator(mode="before")
    def validate_image_source(cls, values):
        image_url = values.get("image_url")
        image_base64 = values.get("image_base64")

        if image_url is not None and image_base64 is not None:
            raise InvalidValueError("Cannot provide both image_url and image_base64")
        elif image_url is None and image_base64 is None:
            raise InvalidValueError("Provide either image_url or image_base64")

        return values
