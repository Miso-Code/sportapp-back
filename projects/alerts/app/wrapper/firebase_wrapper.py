import base64
import json

from firebase_admin import messaging, credentials, initialize_app

from app.config.settings import Config


class FirebaseWrapper:
    def __init__(self):
        self.messaging = messaging
        self.credentials = credentials
        self.initialize_app = initialize_app

    def generate_credentials(self):
        decoded_secret = base64.b64decode(Config.FIREBASE_CERT).decode()
        firebase_cert = json.loads(decoded_secret)
        creds = self.credentials.Certificate(cert=firebase_cert)

        return creds
