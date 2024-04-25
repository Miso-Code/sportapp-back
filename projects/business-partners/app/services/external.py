import requests
import humps

from app.config.settings import Config
from app.models.schemas.schema import PaymentData


class ExternalServices:
    def __init__(self):
        self.miso_stripe_base_url = f"{Config.MISO_STRIPE_BASE_URL}/miso-stripe"

    def process_payment(self, payment_data: PaymentData) -> tuple[bool, dict]:
        response = requests.post(
            f"{self.miso_stripe_base_url}/payments",
            headers={"api_key": Config.MISO_STRIPE_API_KEY},
            json=humps.camelize(payment_data.dict()),
        )
        if response.status_code == 200:
            return True, {}
        return False, response.json()
