import os


class Config:
    EVENTS_API_KEY = os.getenv("EVENTS_API_KEY", "secret")
    # in latitude and longitude degrees, 1 degree is approximately 111.32 km
    EVENT_LOCATION_RADIUS = os.getenv("EVENT_LOCATION_RADIUS", 0.36)  # 40 km
