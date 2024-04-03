import asyncio
import uuid

from fastapi import Depends, APIRouter
from fastapi.responses import JSONResponse
from sqlalchemy.orm import Session
from sse_starlette import EventSourceResponse

from app.config.db import get_db
from app.models.schemas.schema import UserCreate, UserAdditionalInformation
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
                yield "User already exists"
                break
            elif user.email in UserCache.users_success_by_email_map:
                del UserCache.users_success_by_email_map[user.email]
                yield "User created"
                break
            yield "Processing..."
            await asyncio.sleep(1)

    return EventSourceResponse(event_generator(user))


@router.patch("/{user_id}/complete-registration")
async def complete_user_registration(user_id: uuid.UUID, user_additional_information: UserAdditionalInformation, db: Session = Depends(get_db)):
    complete_user_registration_response = UsersService(db).complete_user_registration(user_id, user_additional_information)
    return JSONResponse(content=complete_user_registration_response, status_code=200)
