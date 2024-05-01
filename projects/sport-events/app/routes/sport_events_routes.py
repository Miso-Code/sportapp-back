from typing import Annotated
from uuid import UUID

from fastapi import Depends, APIRouter, Query
from fastapi.responses import JSONResponse
from sqlalchemy.orm import Session

from app.models.schemas.schema import SportEventCreate
from app.services.sport_events import SportEventsService
from app.config.db import get_db

router = APIRouter(
    prefix="/sport-events",
    tags=["sport-events"],
    responses={404: {"description": "Not found"}},
)


@router.post("/")
async def create_sport_event(sport_event_create: SportEventCreate, db: Session = Depends(get_db)):
    sport_event = SportEventsService(db).create_sport_event(sport_event_create)
    return JSONResponse(content=sport_event, status_code=201)


@router.get("/")
async def get_sport_events(
    db: Session = Depends(get_db),
    search: Annotated[str | None, Query(max_length=50)] = None,
    offset: int = Query(0, ge=0, le=1000),
    limit: int = Query(10, gt=0, le=100),
):
    sport_events = SportEventsService(db).get_sport_events(search, offset, limit)
    return JSONResponse(content=sport_events, status_code=200)


@router.get("/{sport_event_id}")
async def get_sport_event(sport_event_id: UUID, db: Session = Depends(get_db)):
    sport_event = SportEventsService(db).get_sport_event(sport_event_id)
    return JSONResponse(content=sport_event, status_code=200)
