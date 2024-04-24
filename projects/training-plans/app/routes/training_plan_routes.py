import uuid
from typing import Annotated

from fastapi import Depends, APIRouter, Header
from fastapi.responses import JSONResponse
from sqlalchemy.orm import Session

from app.config.db import get_db
from app.models.schemas.schema import TrainingPlanCreate
from app.services.training_plan import TrainingPlanService

router = APIRouter(
    prefix="/training-plans",
    tags=["training-plans"],
    responses={404: {"description": "Not found"}},
)


@router.post("/")
async def create_training_plan(training_plan_create: TrainingPlanCreate, user_id: Annotated[uuid.UUID, Header()], db: Session = Depends(get_db)):
    create_training_plan_response = TrainingPlanService(db).generate_training_plan(user_id, training_plan_create)
    return JSONResponse(content=create_training_plan_response, status_code=200)


@router.get("/")
async def get_training_plan(user_id: Annotated[uuid.UUID, Header()], db: Session = Depends(get_db)):
    training_plan = TrainingPlanService(db).get_training_plan(user_id)
    return JSONResponse(content=training_plan, status_code=200)
