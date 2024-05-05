from typing import Annotated
from uuid import UUID

from fastapi import APIRouter, Header, Depends, Query
from fastapi.responses import JSONResponse
from sqlalchemy.orm import Session

from app.config.db import get_db
from app.models.schemas.schema import SessionCalories, NutritionalPlanCreate
from app.services.nutritional_plans import NutritionalPlansService

router = APIRouter(
    prefix="/nutritional-plans",
    tags=["nutritional-plans"],
    responses={404: {"description": "Not found"}},
)


@router.post("/notify-caloric-intake")
async def notify_caloric_intake(
    session_calories: SessionCalories,
    user_id: Annotated[UUID, Header()],
    lang: str = "en",
    authorization: Annotated[str, Header()] = None,
    db: Session = Depends(get_db),
):
    result = NutritionalPlansService(db).notify_caloric_intake(user_id, authorization, session_calories, lang)
    return JSONResponse(content=result)


@router.post("/")
async def create_nutritional_plan(
    user_id: Annotated[UUID, Header()],
    nutritional_plan_create: NutritionalPlanCreate,
    authorization: Annotated[str, Header()] = None,
    db: Session = Depends(get_db),
):
    result = NutritionalPlansService(db).create_nutritional_plan(user_id, authorization, nutritional_plan_create)
    return JSONResponse(content=result, status_code=201)


@router.get("/")
async def get_nutritional_plan(user_id: Annotated[UUID, Header()], lang: str = "en", db: Session = Depends(get_db)):
    result = NutritionalPlansService(db).get_nutritional_plan(user_id, lang)
    return JSONResponse(content=result, status_code=200)
