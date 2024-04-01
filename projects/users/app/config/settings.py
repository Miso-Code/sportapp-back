import os


class Config:
    ACCESS_TOKEN_EXPIRE_MINUTES = int(os.getenv("ACCESS_TOKEN_EXPIRE_MINUTES", 30))
    JWT_ALGORITHM = os.getenv("JWT_ALGORITHM", "HS256")
    JWT_SECRET_KEY = os.getenv("JWT_SECRET_KEY", "secret")
    TOTAL_USERS_BY_RUN = int(os.getenv("TOTAL_USERS_BY_RUN", 50))
    SYNC_EVERY = int(os.getenv("SYNC_EVERY_MINUTES", 2))
