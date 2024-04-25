import os


class Config:
    MISO_STRIPE_API_KEY = os.getenv("MISO_STRIPE_API_KEY", "secret")
    MISO_STRIPE_BASE_URL = os.getenv("SPORTAPP_SERVICES_BASE_URL", "http://localhost:8001")
    BUSINESS_PARTNERS_PRODUCTS_BUCKET_NAME = os.getenv("BUSINESS_PARTNERS_PRODUCTS_BUCKET_NAME", "business-partners-products")
    AWS_REGION = os.getenv("AWS_REGION", "us-east-1")
    ACCESS_TOKEN_EXPIRE_MINUTES = int(os.getenv("ACCESS_TOKEN_EXPIRE_MINUTES", 30))
    REFRESH_TOKEN_EXPIRE_MINUTES = int(os.getenv("REFRESH_TOKEN_EXPIRE_MINUTES", 10080))
    JWT_ALGORITHM = os.getenv("JWT_ALGORITHM", "HS256")
    JWT_SECRET_KEY = os.getenv("JWT_SECRET_KEY", "secret")
