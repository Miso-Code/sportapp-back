import os


class Config:
    HOUR_REGEX = os.getenv("HOUR_REGEX", r"^(1[0-2]|0?[1-9]):([0-5][0-9])\s?(AM|PM)$")
