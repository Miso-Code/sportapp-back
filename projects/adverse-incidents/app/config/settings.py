import os


class Config:
    SPORT_SESSIONS_API_KEY = os.environ.get("SPORT_SESSIONS_API_KEY", "secret")
    ADVERSE_INCIDENTS_PROVIDER_API_KEY = os.environ.get("ADVERSE_INCIDENTS_PROVIDER_API_KEY", "secret")
    NOTIFIER_SLEEP_TIME_SECONDS = int(os.environ.get("NOTIFIER_SLEEP_TIME_SECONDS", 180))
    SPORTAPP_SERVICES_BASE_URL = os.environ.get("SPORTAPP_SERVICES_BASE_URL", "http://localhost:8000")
    ADVERSE_INCIDENTS_ALERTS_QUEUE = os.environ.get("ADVERSE_INCIDENTS_ALERTS_QUEUE", "adverse_incidents_queue.fifo")
    AWS_REGION = os.getenv("AWS_REGION", "us-east-1")
