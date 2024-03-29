import os


class Config:
    SPORT_SESSION_URL = os.getenv('SPORT_SESSION_URL', 'http://localhost:3003/sport-session')
    ADVERSE_INCIDENTS_PROVIDER_URL = os.getenv('ADVERSE_INCIDENTS_PROVIDER_URL', 'http://localhost:4000/incidents')
    ADVERSE_INCIDENTS_PROVIDER_REFRESH_INTERVAL_SECONDS = int(
        os.getenv('ADVERSE_INCIDENTS_PROVIDER_REFRESH_INTERVAL_SECONDS', 5))
    ADVERSE_INCIDENTS_PROVIDER_API_KEY = os.getenv('ADVERSE_INCIDENTS_PROVIDER_API_KEY', '1234')
    AWS_REGION = os.getenv('AWS_REGION', 'us-east-1')
    NOTIFICATION_SQS_QUEUE = os.getenv('NOTIFICATION_SQS_QUEUE', 'adverse_incidents_queue.fifo')
