import os


class Config:
    FIREBASE_CERT = os.getenv("FIREBASE_CERT", "")
    ADVERSE_INCIDENTS_ALERTS_QUEUE = os.environ.get("ADVERSE_INCIDENTS_ALERTS_QUEUE", "adverse_incidents_queue.fifo")
    NUTRITIONAL_PLAN_ALERTS_QUEUE = os.environ.get("NUTRITIONAL_PLAN_ALERTS_QUEUE", "nutritional_plan_queue.fifo")
    AWS_REGION = os.getenv("AWS_REGION", "us-east-1")
