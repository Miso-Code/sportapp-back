from sqlalchemy.orm import Session

from ..models.model import UserAlertDevice
from ..models.schemas.schema import UserAlertDeviceCreate


class AlertService:
    def __init__(self, db: Session):
        self.db = db

    def register_device(self, alert_data: UserAlertDeviceCreate):
        alert = UserAlertDevice(user_id=alert_data.user_id, device_token=alert_data.device_token, enabled=alert_data.enabled)
        self.db.add(alert)
        self.db.commit()
        self.db.refresh(alert)
        return alert
