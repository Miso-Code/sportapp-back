from pydantic import BaseModel


class AdverseIncidentMessage(BaseModel):
    message: str
    user_id: str
    date: str


class AdverseIncidentBoundingBox(BaseModel):
    latitude_from: float
    latitude_to: float
    longitude_from: float
    longitude_to: float


class AdverseIncident(BaseModel):
    description: str
    bounding_box: AdverseIncidentBoundingBox


class UserTraining(BaseModel):
    user_id: str
    latitude: float
    longitude: float
