from typing import Optional

from pydantic import BaseModel


class UserAlertDeviceCreate(BaseModel):
    device_token: str
    enabled: Optional[bool] = True


class TestAlert(BaseModel):
    device_token: str
    title: str
    message: str
    priority: str
