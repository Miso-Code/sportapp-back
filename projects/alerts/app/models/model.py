from dataclasses import dataclass
from uuid import UUID

from sqlalchemy import Column, String, Uuid, Boolean

from app.config.db import base


@dataclass
class UserAlertDevice(base):
    __tablename__ = "user_alert_devices"

    user_id: UUID = Column(Uuid(as_uuid=True), primary_key=True, nullable=False)
    device_token: str = Column(String, nullable=False)
    enabled: bool = Column(Boolean, default=True)
