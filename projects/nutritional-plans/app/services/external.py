from uuid import UUID

import requests

from app.config.settings import Config
from app.exceptions.exceptions import ExternalServiceError


class ExternalServices:
    def __init__(self):
        self.users_base_url = f"{Config.SPORTAPP_SERVICES_BASE_URL}/users"
        self.training_plan_base_url = f"{Config.SPORTAPP_SERVICES_BASE_URL}/training-plans"

    def get_user_sport_profile(self, user_id: UUID, user_auth_token: str) -> dict:
        response = requests.get(f"{self.users_base_url}/profiles/sports", headers={"Authorization": user_auth_token})
        if response.status_code == 200:
            return response.json()
        raise ExternalServiceError(f"Error calling user_sport_profile for user {user_id}: {response.status_code} - {response.json()}")

    def get_training_plan(self, user_id, user_auth_token):
        response = requests.get(f"{self.training_plan_base_url}", headers={"Authorization": user_auth_token})
        if response.status_code == 200:
            return response.json()
        raise ExternalServiceError(f"Error calling training_plan for user {user_id}: {response.status_code} - {response.json()}")
