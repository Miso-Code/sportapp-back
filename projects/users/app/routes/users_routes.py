import asyncio

from fastapi import Depends, APIRouter
from fastapi.responses import JSONResponse
from sqlalchemy.orm import Session
from sse_starlette import EventSourceResponse

from ..config.db import get_db
from ..models.schemas.schema import UserCreate, UserCredentials
from ..services.users import UsersService
from ..utils.user_cache import UserCache

router = APIRouter(
    prefix="/users",
    tags=["users"],
    responses={404: {"description": "Not found"}},
)


@router.post("/")
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
async def complete_user_registration(user_id: str, db: Session = Depends(get_db)):
    user_created_response = UsersService(db).complete_user_registration(user_id)
    return JSONResponse(content=user_created_response, status_code=200)
