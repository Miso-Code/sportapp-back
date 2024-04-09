import asyncio
import json
import uuid

from fastapi import Depends, APIRouter
from fastapi.responses import JSONResponse
from sqlalchemy.orm import Session
from sse_starlette import EventSourceResponse

from app.config.db import get_db
from app.models.schemas.schema import UserCreate, UserAdditionalInformation, UserCredentials
from app.services.users import UsersService
from app.utils.user_cache import UserCache

router = APIRouter(
    prefix="/users",
    tags=["users"],
    responses={404: {"description": "Not found"}},
)


@router.post("")
async def register_user(user: UserCreate):
    UserCache.users.append(user)

    async def event_generator(user):
        while True:
            if user.email in UserCache.users_with_errors_by_email_map:
                del UserCache.users_with_errors_by_email_map[user.email]
                response = {"status": "error", "message": "User already exists"}
                yield json.dumps(response)
                break
            elif user.email in UserCache.users_success_by_email_map:
                user_created = UserCache.users_success_by_email_map[user.email]
                del UserCache.users_success_by_email_map[user.email]
                response = {
                    "status": "success",
                    "message": "User created",
                    "data": {
                        "id": user_created["user_id"],
                        "email": user_created["email"],
                        "first_name": user_created["first_name"],
                        "last_name": user_created["last_name"],
                    },
                }
                yield json.dumps(response)
                break
            response = {"status": "processing", "message": "Processing..."}
            yield json.dumps(response)
            await asyncio.sleep(1)

    return EventSourceResponse(event_generator(user))


@router.post("/login")
async def login_user(user_credentials: UserCredentials, db: Session = Depends(get_db)):
    login_user_response = UsersService(db).authenticate_user(user_credentials)
    return JSONResponse(content=login_user_response, status_code=200)


@router.patch("/{user_id}/complete-registration")
async def complete_user_registration(user_id: uuid.UUID, user_additional_information: UserAdditionalInformation, db: Session = Depends(get_db)):
    complete_user_registration_response = UsersService(db).complete_user_registration(user_id, user_additional_information)
    return JSONResponse(content=complete_user_registration_response, status_code=200)


@router.get("/profiles/{user_id}/personal")
async def get_user_personal_information(user_id: uuid.UUID, db: Session = Depends(get_db)):
    user_personal_information = UsersService(db).get_user_personal_information(user_id)
    return JSONResponse(content=user_personal_information, status_code=200)


@router.get("/profiles/{user_id}/sports")
async def get_user_sports_information(user_id: uuid.UUID, db: Session = Depends(get_db)):
    user_sports_information = UsersService(db).get_user_sports_information(user_id)
    return JSONResponse(content=user_sports_information, status_code=200)
