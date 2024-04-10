import os


class Config:
    SYNC_USERS = os.getenv("SYNC_USERS", True)
    AVG_STEP_LENGTH = float(os.getenv("AVG_STEP_LENGTH", 0.762))
    AVG_CALORIES_PER_STEP = float(os.getenv("AVG_CALORIES_PER_STEP", 0.04))
