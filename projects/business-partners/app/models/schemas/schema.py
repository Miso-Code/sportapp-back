from datetime import datetime
from typing import Optional
from uuid import UUID

from pydantic import BaseModel, model_validator
from app.exceptions.exceptions import InvalidValueError
from app.models.business_partners import ProductCategory, PaymentType, PaymentFrequency, TransactionStatus


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
    summary: str
    url: str
    price: float
    payment_type: PaymentType
    payment_frequency: PaymentFrequency
    image_url: Optional[str] = None
    image_base64: Optional[str] = None
    description: str
    active: Optional[bool] = None

    @model_validator(mode="before")
    def validate_image_source(cls, values):
        image_url = values.get("image_url")
        image_base64 = values.get("image_base64")

        if image_url is not None and image_base64 is not None:
            raise InvalidValueError("Cannot provide both image_url and image_base64")
        elif image_url is None and image_base64 is None:
            raise InvalidValueError("Provide either image_url or image_base64")

        return values


class UpdateBusinessPartnerProduct(BaseModel):
    category: Optional[ProductCategory] = None
    name: Optional[str] = None
    summary: Optional[str] = None
    url: Optional[str] = None
    price: Optional[float] = None
    payment_type: Optional[PaymentType] = None
    payment_frequency: Optional[PaymentFrequency] = None
    image_url: Optional[str] = None
    image_base64: Optional[str] = None
    description: Optional[str] = None
    active: Optional[bool] = None


class PaymentData(BaseModel):
    card_number: str
    card_holder: str
    card_expiration_date: str
    card_cvv: str
    amount: float


class ProductPurchase(BaseModel):
    user_name: str
    user_email: str
    payment_data: PaymentData


class TransactionResponse(BaseModel):
    transaction_id: UUID
    transaction_status: TransactionStatus
    transaction_date: datetime
    message: str
