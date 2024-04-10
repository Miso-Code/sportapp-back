import datetime
import re
from typing import Optional

from pydantic import BaseModel, UUID4, conint, confloat


class SportSessionLocationCreate(BaseModel):
    latitude: float
    longitude: float
    accuracy: Optional[float] = None
    altitude: Optional[float] = None
    altitude_accuracy: Optional[float] = None
    heading: Optional[float] = None
    speed: Optional[float] = None


class SportSessionFinish(BaseModel):
    duration: conint(gt=0)
    steps: Optional[conint(ge=0)] = None
    distance: Optional[confloat(gt=0)] = None
    calories: Optional[confloat(gt=0)] = None
    average_speed: Optional[confloat(gt=0)] = None
    min_heartrate: Optional[confloat(gt=0)] = None
    max_heartrate: Optional[confloat(gt=0)] = None
    avg_heartrate: Optional[confloat(gt=0)] = None


class SportSessionStart(BaseModel):
    sport_id: UUID4
    user_id: UUID4
    started_at: datetime.datetime
    initial_location: SportSessionLocationCreate
