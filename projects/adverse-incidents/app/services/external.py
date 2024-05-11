import requests

from app.config.settings import Config
from app.exceptions.exceptions import ExternalServiceError


class ExternalServices:
    def __init__(self):
        self.adverse_incidents_provider_url = f"{Config.SPORTAPP_SERVICES_BASE_URL}/incidents"
        self.sport_sessions_url = f"{Config.SPORTAPP_SERVICES_BASE_URL}/sport-sessions"

    def get_incidents(self):
        response = requests.get(self.adverse_incidents_provider_url, headers={"x-api-key": Config.ADVERSE_INCIDENTS_PROVIDER_API_KEY})
        if response.status_code == 200:
            return response.json()
        raise ExternalServiceError(f"Failed to get incidents: {response.json()}")

    def get_users_training(self):
        response = requests.get(f"{self.sport_sessions_url}/active-sport-sessions", headers={"x-api-key": Config.SPORT_SESSIONS_API_KEY})
        if response.status_code == 200:
            return response.json()
        raise ExternalServiceError(f"Failed to get users training: {response.json()}")
