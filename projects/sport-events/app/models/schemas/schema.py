import datetime

from pydantic import BaseModel, conint, UUID4


class SportEventCreate(BaseModel):
    sport_id: UUID4
    location_latitude: float
    location_longitude: float
    start_date: datetime.datetime
    end_date: datetime.datetime
    title: str
    capacity: conint(gt=0)
    description: str
