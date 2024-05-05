import os


class Config:
    CALORIES_TOLERANCE = os.getenv("CALORIES_TOLERANCE", 100)
    SPORTAPP_SERVICES_BASE_URL = os.getenv("SPORTAPP_SERVICES_BASE_URL", "http://localhost:8001")
    NUTRITIONAL_PLAN_ALERTS_QUEUE = os.getenv("NUTRITIONAL_PLAN_ALERTS_QUEUE", "nutritional-plan-alerts")
    AWS_REGION = os.getenv("AWS_REGION", "us-east-1")
