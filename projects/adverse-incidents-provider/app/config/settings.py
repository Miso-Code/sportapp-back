import os

from app.models.schemas.schema import Coordinate


class Config:
    MAX_ADVERSE_INCIDENTS = os.getenv("MAX_ADVERSE_INCIDENTS", 5)
    ADVERSE_INCIDENTS_AFFECTED_RANGE = os.getenv("ADVERSE_INCIDENTS_AFFECTED_RANGE", 0.5)
    INCIDENTS_API_KEY = os.getenv("INCIDENTS_API_KEY", "secret")
    CALI_BOUNDARY_CODES = [
        Coordinate(latitude=-76.8635495958, longitude=3.1194990575),
        Coordinate(latitude=-76.8642836451, longitude=3.8006769776),
        Coordinate(latitude=-76.0888693083, longitude=3.8015092147),
        Coordinate(latitude=-76.088135259, longitude=3.1203318932),
        Coordinate(latitude=-76.8635495958, longitude=3.1194990575),
    ]
