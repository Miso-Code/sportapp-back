from typing import Annotated

from fastapi import Depends, APIRouter, Header
from fastapi.responses import JSONResponse
from sqlalchemy.orm import Session
from pydantic import UUID4

from app.models.schemas.schema import SportSessionFinish, SportSessionStart, SportSessionLocationCreate
from app.services.sport_sessions import SportSessionService
from app.config.db import get_db
from app.config.settings import Config
from app.utils import utils

router = APIRouter(
    prefix="/sport-session",
    tags=["sport-session"],
    responses={404: {"description": "Not found"}},
)


@router.post("/")
async def start_sport_session(sport_session: SportSessionStart, user_id: Annotated[UUID4 | None, Header()] = None, db: Session = Depends(get_db)):
    if user_id and str(user_id) != str(sport_session.user_id):
        return JSONResponse(content={"error": Config.NO_OWNER_MESSAGE}, status_code=403)

    sport_session = SportSessionService(db).start_sport_session(sport_session)
    return JSONResponse(content=sport_session, status_code=200)


@router.get("/")
async def get_all_sport_sessions(user_id: Annotated[UUID4 | None, Header()] = None, db: Session = Depends(get_db)):
    sport_sessions = SportSessionService(db).get_sport_sessions(user_id)
    return JSONResponse(content=sport_sessions, status_code=200)


@router.get("/active-sport-sessions")
async def get_active_sport_sessions(db: Session = Depends(get_db), x_api_key: Annotated[str | None, Header()] = None):
    utils.validate_api_key(x_api_key)
    sport_sessions = SportSessionService(db).get_active_sport_sessions()
    return JSONResponse(content=sport_sessions, status_code=200)


@router.put("/{sport_session_id}/location")
async def add_locations_to_sport_session(
    sport_session_id: UUID4,
    location: SportSessionLocationCreate,
    user_id: Annotated[UUID4 | None, Header()] = None,
    db: Session = Depends(get_db),
):
    if user_id:
        sport_session = SportSessionService(db).get_sport_session(sport_session_id)
        if sport_session["user_id"] != str(user_id):
            return JSONResponse(content={"error": Config.NO_OWNER_MESSAGE}, status_code=403)

    sport_session = SportSessionService(db).add_location_to_sport_session(sport_session_id, location)
    return JSONResponse(content=sport_session, status_code=200)


@router.patch("/{sport_session_id}")
async def finish_sport_session(sport_session_id: UUID4, sport_session_input: SportSessionFinish, user_id: Annotated[UUID4 | None, Header()] = None, db: Session = Depends(get_db)):
    if user_id:
        sport_session = SportSessionService(db).get_sport_session(sport_session_id)
        if sport_session["user_id"] != str(user_id):
            return JSONResponse(content={"error": Config.NO_OWNER_MESSAGE}, status_code=403)

    sport_session = SportSessionService(db).finish_sport_session(sport_session_id, sport_session_input)
    return JSONResponse(content=sport_session, status_code=200)


@router.get("/{sport_session_id}")
async def get_sport_session(sport_session_id: UUID4, user_id: Annotated[UUID4 | None, Header()] = None, db: Session = Depends(get_db)):
    sport_session = SportSessionService(db).get_sport_session(sport_session_id)

    if user_id:
        if sport_session["user_id"] != str(user_id):
            return JSONResponse(content={"error": Config.NO_OWNER_MESSAGE}, status_code=403)

    return JSONResponse(content=sport_session, status_code=200)
