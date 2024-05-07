from http import HTTPStatus
from typing import Annotated
from uuid import UUID

from fastapi import Depends, APIRouter, Header
from sqlalchemy.orm import Session
from fastapi.responses import JSONResponse

from app.config.db import get_db
from app.models.schemas.schema import UserAlertDeviceCreate, TestAlert
from app.services.alerts import AlertsService

router = APIRouter(
    prefix="/alerts",
    tags=["alerts"],
    responses={404: {"description": "Not found"}},
)


@router.post("/register-device")
async def register_device(user_device: UserAlertDeviceCreate, user_id: Annotated[UUID, Header()], db: Session = Depends(get_db)):
    register_device_response = AlertsService(db).register_device(user_id, user_device)
    return JSONResponse(content=register_device_response, status_code=HTTPStatus.CREATED)


@router.put("/disable-device")
async def disable_device(user_id: Annotated[UUID, Header()], db: Session = Depends(get_db)):
    disable_device_response = AlertsService(db).disable_device(user_id)
    return JSONResponse(content=disable_device_response, status_code=HTTPStatus.OK)


@router.get("/device")
async def get_user_device(user_id: Annotated[UUID, Header()], db: Session = Depends(get_db)):
    get_device_response = AlertsService(db).get_user_device(user_id)
    return JSONResponse(content=get_device_response, status_code=HTTPStatus.OK)


@router.post("/send-test-alert")
async def send_test_alert(user_id: Annotated[UUID, Header()], message_data: TestAlert, db: Session = Depends(get_db)):
    test_alert_response = AlertsService(db).send_test_alert(message_data)
    return JSONResponse(content=test_alert_response, status_code=HTTPStatus.OK)
