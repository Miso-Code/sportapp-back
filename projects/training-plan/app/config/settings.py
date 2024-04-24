import os


class Config:
    EMAIL_REGEX = os.getenv("EMAIL_REGEX", r"[^@]+@[^@]+\.[^@]+")  # TODO REMOVE
