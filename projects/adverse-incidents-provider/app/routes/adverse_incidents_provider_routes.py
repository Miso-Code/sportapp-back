from typing import List

from fastapi import APIRouter
from fastapi.responses import JSONResponse

from app.models.schemas.schema import Coordinate
from app.services.adverse_incidents_provider import AdverseIncidentsProviderService

router = APIRouter(
    prefix="/incidents",
    tags=["adverse-incidents-provider"],
    responses={404: {"description": "Not found"}},
)


@router.post("/")
async def generate_incidents(coordinates: List[Coordinate] | None = None):
    random_incidents = AdverseIncidentsProviderService.randomize_adverse_incidents(coordinates)
    return JSONResponse(content=random_incidents, status_code=200)
