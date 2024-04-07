from sqlalchemy import Column, String, Uuid, Boolean
from ..config.db import base


class UserAlertDevice(base):
    __tablename__ = "user_alert_devices"

    user_id = Column(Uuid(as_uuid=True), primary_key=True, nullable=False)
    device_token = Column(String, primary_key=True, nullable=False)
    enabled = Column(Boolean, default=True)
