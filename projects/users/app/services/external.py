import requests
import humps

from app.config.settings import Config
from app.exceptions.exceptions import NotFoundError
from app.models.schemas.schema import PaymentData


class ExternalServices:
    def __init__(self):
        self.sports_url = f"{Config.SPORTAPP_SERVICES_BASE_URL}/sports"
        self.training_plans_url = f"{Config.SPORTAPP_SERVICES_BASE_URL}/training-plans"
        self.miso_stripe_url = f"{Config.SPORTAPP_SERVICES_BASE_URL}/miso-stripe"

    def get_sport(self, sport_id: str, user_token: str):
        if not user_token:
            raise NotFoundError(f"Sport with id {sport_id} not found")
        response = requests.get(f"{self.sports_url}/{sport_id}", headers={"Authorization": user_token})
        if response.status_code == 200:
            return response.json()
        raise NotFoundError(f"Sport with id {sport_id} not found")

    def create_training_plan(self, training_plan_data: dict, user_token: str):
        response = requests.post(self.training_plans_url, json=training_plan_data, headers={"Authorization": user_token})
        if response.status_code == 200:
            return response.json()
        raise NotFoundError("Failed to create training plan")

    def process_payment(self, payment_data: PaymentData) -> tuple[bool, dict]:
        response = requests.post(
            f"{self.miso_stripe_url}/payments",
            headers={"api_key": Config.MISO_STRIPE_API_KEY},
            json=humps.camelize(payment_data.dict()),
        )
        if response.status_code == 200:
            return True, {}
        return False, response.json()
