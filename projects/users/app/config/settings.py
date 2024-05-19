import os


class Config:
    SPORTAPP_SERVICES_BASE_URL = os.getenv("SPORTAPP_SERVICES_BASE_URL", "http://localhost:8001")
    MISO_STRIPE_API_KEY = os.getenv("MISO_STRIPE_API_KEY", "secret")
    SYNC_USERS = os.getenv("SYNC_USERS", True)
    ACCESS_TOKEN_EXPIRE_MINUTES = int(os.getenv("ACCESS_TOKEN_EXPIRE_MINUTES", 30))
    REFRESH_TOKEN_EXPIRE_MINUTES = int(os.getenv("REFRESH_TOKEN_EXPIRE_MINUTES", 10080))
    JWT_ALGORITHM = os.getenv("JWT_ALGORITHM", "HS256")
    JWT_SECRET_KEY = os.getenv("JWT_SECRET_KEY", "secret")
    TOTAL_USERS_BY_RUN = int(os.getenv("TOTAL_USERS_BY_RUN", 50))
    SYNC_EVERY = int(os.getenv("SYNC_EVERY_MINUTES", 2))
    PASSWORD_REGEX = os.getenv("PASSWORD_REGEX", r"((?=.*\d)(?=.*[a-z])(?=.*[A-Z])(?=.*[\W]).{8,64})")
    EMAIL_REGEX = os.getenv("EMAIL_REGEX", r"[^@]+@[^@]+\.[^@]+")
    HOUR_REGEX = os.getenv("HOUR_REGEX", r"^(1[0-2]|0?[1-9]):([0-5][0-9])\s?(AM|PM)$")
