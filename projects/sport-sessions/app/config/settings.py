import os


class Config:
    SPORT_SESSIONS_API_KEY = os.getenv("SPORT_SESSIONS_API_KEY", "secret")
    SYNC_USERS = os.getenv("SYNC_USERS", True)
    AVG_STEP_LENGTH = float(os.getenv("AVG_STEP_LENGTH", 0.762))
    AVG_CALORIES_PER_STEP = float(os.getenv("AVG_CALORIES_PER_STEP", 0.04))
    NO_OWNER_MESSAGE = os.getenv("NO_OWNER_MESSAGE", "User is not the owner of the sport session")
    NOT_FOUND_MESSAGE = os.getenv("NOT_FOUND_MESSAGE", "Sport session not found")
