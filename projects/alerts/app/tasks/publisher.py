from app.config.db import get_db
from app.firebase.firebase import FirebaseClient
from app.services.alerts import AlertsService


class Publisher:

    @staticmethod
    def send_alert(user_id: str, priority: str, title: str, message: str):
        db = get_db()
        alerts_service = AlertsService(db)
        try:
            user_device = alerts_service.get_user_device(user_id)
            user_device_token = user_device["device_token"]
            FirebaseClient.send_fcm_alert(user_device_token, priority, title, message)
        except Exception as e:
            print(f"User device not found, skipping push notification: {e}")
