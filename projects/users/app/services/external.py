import requests

from app.config.settings import Config
from app.exceptions.exceptions import NotFoundError


class ExternalServices:
    def __init__(self):
        self.sports_url = Config.SPORTAPP_SERVICES_BASE_URL
        self.training_plans_url = Config.SPORTAPP_SERVICES_BASE_URL

    def get_sport(self, sport_id: str, user_token: str):
        if not user_token:
            raise NotFoundError(f"Sport with id {sport_id} not found")
        response = requests.get(f"{self.sports_url}/sports/{sport_id}", headers={"Authorization": user_token})
        if response.status_code == 200:
            return response.json()
        raise NotFoundError(f"Sport with id {sport_id} not found")

    def create_training_plan(self, training_plan_data: dict, user_token: str):
        response = requests.post(f"{self.training_plans_url}/training-plans/", json=training_plan_data, headers={"Authorization": user_token})
        if response.status_code == 200:
            return response.json()
        raise NotFoundError("Failed to create training plan")
