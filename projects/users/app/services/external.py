import requests

from app.config.settings import Config
from app.exceptions.exceptions import NotFoundError


class ExternalServices:
    def __init__(self):
        self.sports_url = Config.SPORTS_URL

    def get_sport(self, sport_id):
        response = requests.get(f"{self.sports_url}/sports/{sport_id}")
        if response.status_code == 200:
            return response.json()
        raise NotFoundError(f"Sport with id {sport_id} not found")
