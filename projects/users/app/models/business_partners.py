from dataclasses import dataclass
from uuid import uuid4, UUID

from sqlalchemy import Column, Uuid, String

from app.config.db import base

BUSINESS_PARTNER_SCOPE = "business_partner"


@dataclass
class BusinessPartner(base):
    __tablename__ = "business_partners"
    business_partner_id: UUID = Column(Uuid(as_uuid=True), primary_key=True, default=uuid4)
    business_partner_name: str = Column(String, nullable=False)
    email: str = Column(String, nullable=False, unique=True)
    hashed_password: str = Column(String, nullable=False)
