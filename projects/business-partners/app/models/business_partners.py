import enum
from dataclasses import dataclass
from uuid import uuid4, UUID

from sqlalchemy import Column, Uuid, String, Enum, Float, ForeignKey, Boolean
from sqlalchemy.orm import relationship

from app.config.db import base

BUSINESS_PARTNER_SCOPE = "business_partner"


class ProductCategory(enum.Enum):
    EQUIPMENT = "equipment"
    APPAREL = "apparel"
    NUTRITION = "nutrition"
    TRAINING_SERVICES = "training_services"
    WELLNESS = "wellness"
    SPORTS_TECHNOLOGY = "sports_technology"
    MEDICAL_SERVICES = "medical_services"


class PaymentType(enum.Enum):
    UNIQUE = "unique"
    PERIODIC = "periodic"


class PaymentFrequency(enum.Enum):
    WEEKLY = "weekly"
    MONTHLY = "monthly"
    ANNUALLY = "annually"
    BI_ANNUALLY = "bi_annually"
    QUARTERLY = "quarterly"
    OTHER = "other"


@dataclass
class BusinessPartner(base):
    __tablename__ = "business_partners"
    business_partner_id: UUID = Column(Uuid(as_uuid=True), primary_key=True, default=uuid4)
    business_partner_name: str = Column(String, nullable=False)
    email: str = Column(String, nullable=False, unique=True)
    hashed_password: str = Column(String, nullable=False)
    products = relationship("BusinessPartnerProduct", backref="business_partner")


@dataclass
class BusinessPartnerProduct(base):
    __tablename__ = "business_partner_products"
    product_id: UUID = Column(Uuid(as_uuid=True), primary_key=True, default=uuid4)
    business_partner_id: UUID = Column("business_partner_id", ForeignKey("business_partners.business_partner_id"), nullable=False)
    category: ProductCategory = Column(Enum(ProductCategory), nullable=False)
    name: str = Column(String, nullable=False)
    url: str = Column(String, nullable=False)
    price: Float = Column(Float, nullable=False)
    payment_type: PaymentType = Column(Enum(PaymentType), nullable=False)
    payment_frequency: PaymentFrequency = Column(Enum(PaymentFrequency), nullable=True)
    image_url: str = Column(String, nullable=True)
    description: str = Column(String, nullable=False)
    active: bool = Column(Boolean, nullable=False, default=True)
