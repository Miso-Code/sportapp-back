from dataclasses import asdict
from uuid import UUID

from sqlalchemy.orm import Session

from app.exceptions.exceptions import NotFoundError
from app.models.mappers.data_mapper import DataClassMapper
from app.models.model import UserAlertDevice
from app.models.schemas.schema import UserAlertDeviceCreate


class AlertsService:
    def __init__(self, db: Session):
        self.db = db

    def register_device(self, user_id: UUID, alert_data: UserAlertDeviceCreate):
        device = self.db.query(UserAlertDevice).filter(UserAlertDevice.user_id == user_id).first()
        if device:
            device.device_token = alert_data.device_token
            device.enabled = alert_data.enabled
        else:
            device = UserAlertDevice(user_id=user_id, device_token=alert_data.device_token)
            self.db.add(device)
        self.db.commit()

        return DataClassMapper.to_dict(device)

    def get_user_device(self, user_id):
        device = self.db.query(UserAlertDevice).filter(UserAlertDevice.user_id == user_id).first()
        if not device:
            raise NotFoundError(f"User {user_id} has no registered devices")

        return DataClassMapper.to_dict(device)

    def disable_device(self, user_id):
        device = self.db.query(UserAlertDevice).filter(UserAlertDevice.user_id == user_id).first()
        if not device:
            raise NotFoundError(f"User {user_id} has no registered devices")
        device.enabled = False
        self.db.commit()

        return DataClassMapper.to_dict(device)
