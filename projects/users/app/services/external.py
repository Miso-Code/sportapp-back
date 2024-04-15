import requests

from app.config.settings import Config
from app.exceptions.exceptions import NotFoundError


class ExternalServices:
    def __init__(self):
        self.sports_url = Config.SPORTAPP_SERVICES_BASE_URL

    def get_sport(self, sport_id: str, user_token: str):
        if not user_token:
            raise NotFoundError(f"Sport with id {sport_id} not found")
        response = requests.get(f"{self.sports_url}/sports/{sport_id}", headers={"Authorization": user_token})
        if response.status_code == 200:
            return response.json()
        raise NotFoundError(f"Sport with id {sport_id} not found")
