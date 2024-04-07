from http import HTTPStatus

from fastapi import Depends, APIRouter
from sqlalchemy.orm import Session
from starlette.responses import JSONResponse

from app.config.db import get_db
from app.models.schemas.schema import UserAlertDeviceCreate
from app.services.alerts import AlertService

router = APIRouter(
    prefix="/alerts",
    tags=["alerts"],
    responses={404: {"description": "Not found"}},
)


@router.post("/register-device")
async def register_device(user_device: UserAlertDeviceCreate, db: Session = Depends(get_db)):
    register_device_response = AlertService(db).register_device(user_device)
    return JSONResponse(content=register_device_response, status_code=HTTPStatus.CREATED)
