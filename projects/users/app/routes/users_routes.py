import asyncio
import json
import uuid
from typing import Annotated

from fastapi import Depends, APIRouter, Header
from fastapi.responses import JSONResponse
from sqlalchemy.orm import Session
from sse_starlette import EventSourceResponse

from app.config.db import get_db
from app.models.schemas.profiles_schema import UserPersonalProfile, UserNutritionalProfile, UserSportsProfileUpdate
from app.models.schemas.schema import UserCreate, UserAdditionalInformation, UserCredentials, UpdateSubscriptionType
from app.services.users import UsersService
from app.utils.user_cache import UserCache

router = APIRouter(
    prefix="/users",
    tags=["users"],
    responses={404: {"description": "Not found"}},
)


@router.post("/registration")
async def register_user(user: UserCreate):
    UserCache.users.append(user)

    async def event_generator(user_to_add):
        while True:
            if user_to_add.email in UserCache.users_with_errors_by_email_map:
                del UserCache.users_with_errors_by_email_map[user_to_add.email]
                response = {"status": "error", "message": "User already exists"}
                yield json.dumps(response)
                break
            elif user_to_add.email in UserCache.users_success_by_email_map:
                user_created = UserCache.users_success_by_email_map[user_to_add.email]
                del UserCache.users_success_by_email_map[user_to_add.email]
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


@router.patch("/complete-registration")
async def complete_user_registration(user_additional_information: UserAdditionalInformation, user_id: Annotated[uuid.UUID, Header()], db: Session = Depends(get_db)):
    complete_user_registration_response = UsersService(db).complete_user_registration(user_id, user_additional_information)
    return JSONResponse(content=complete_user_registration_response, status_code=200)


@router.get("/profiles/personal")
async def get_user_personal_information(user_id: Annotated[uuid.UUID, Header()], db: Session = Depends(get_db)):
    user_personal_information = UsersService(db).get_user_personal_information(user_id)
    return JSONResponse(content=user_personal_information, status_code=200)


@router.get("/profiles/sports")
async def get_user_sports_information(user_id: Annotated[uuid.UUID, Header()], db: Session = Depends(get_db)):
    user_sports_information = UsersService(db).get_user_sports_information(user_id)
    return JSONResponse(content=user_sports_information, status_code=200)


@router.get("/profiles/nutritional")
async def get_user_nutritional_information(user_id: Annotated[uuid.UUID, Header()], db: Session = Depends(get_db)):
    user_nutritional_information = UsersService(db).get_user_nutritional_information(user_id)
    return JSONResponse(content=user_nutritional_information, status_code=200)


@router.patch("/profiles/personal")
async def update_user_personal_information(personal_profile: UserPersonalProfile, user_id: Annotated[uuid.UUID, Header()], db: Session = Depends(get_db)):
    user_personal_information = UsersService(db).update_user_personal_information(user_id, personal_profile)
    return JSONResponse(content=user_personal_information, status_code=200)


@router.patch("/profiles/sports")
async def update_user_sports_information(
    sports_profile: UserSportsProfileUpdate,
    user_id: Annotated[uuid.UUID, Header()],
    authorization: Annotated[str, Header()] = None,
    db: Session = Depends(get_db),
):
    user_sports_information = UsersService(db, authorization).update_user_sports_information(user_id, sports_profile)
    return JSONResponse(content=user_sports_information, status_code=200)


@router.patch("/profiles/nutritional")
async def update_user_nutritional_information(nutritional_profile: UserNutritionalProfile, user_id: Annotated[uuid.UUID, Header()], db: Session = Depends(get_db)):
    user_nutritional_information = UsersService(db).update_user_nutritional_information(user_id, nutritional_profile)
    return JSONResponse(content=user_nutritional_information, status_code=200)


@router.get("/nutritional-limitations")
async def get_nutritional_limitations(db: Session = Depends(get_db)):
    nutritional_limitations = UsersService(db).get_nutritional_limitations()
    return JSONResponse(content=nutritional_limitations, status_code=200)


@router.patch("/update-plan")
async def update_user_plan(user_id: Annotated[uuid.UUID, Header()], update_subscription_type: UpdateSubscriptionType, db: Session = Depends(get_db)):
    user_plan = UsersService(db).update_user_plan(user_id, update_subscription_type)
    return JSONResponse(content=user_plan, status_code=200)
