import os


class Config:
    EVENTS_API_KEY = os.getenv("EVENTS_API_KEY", "secret")
