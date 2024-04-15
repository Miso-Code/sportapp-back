from fastapi import Depends, APIRouter
from fastapi.responses import JSONResponse
from sqlalchemy.orm import Session
from pydantic import UUID4

from ..services.sports import SportService
from ..config.db import get_db

router = APIRouter(
    prefix="/sports",
    tags=["sports"],
    responses={404: {"description": "Not found"}},
)


@router.get("/")
async def get_all_sports(db: Session = Depends(get_db)):
    sports = SportService(db).get_sports()
    return JSONResponse(content=sports, status_code=200)


@router.get("/{sport_id}")
async def get_sport_by_id(sport_id: UUID4, db: Session = Depends(get_db)):
    sport = SportService(db).get_sport_by_id(sport_id)
    return JSONResponse(content=sport, status_code=200)
