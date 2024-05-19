from typing import List, Optional

from pydantic import BaseModel


class BoundingBox(BaseModel):
    latitude_from: float
    longitude_from: float
    latitude_to: float
    longitude_to: float


class AdverseIncident(BaseModel):
    description: str
    bounding_box: BoundingBox


class Coordinate(BaseModel):
    longitude: float
    latitude: float
