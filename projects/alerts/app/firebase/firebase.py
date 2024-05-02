from firebase_admin import messaging


def _build_message(device_registration_token: str, priority: str, title: str, message: str):
    notification = messaging.Notification(title=title, body=message)
    android_config = messaging.AndroidConfig(priority=priority)

    return messaging.Message(notification=notification, token=device_registration_token, android=android_config)


class FirebaseClient:

    @staticmethod
    def send_fcm_alert(device_registration_token: str, priority: str, title: str, message_data: str):
        if not device_registration_token:
            return

        message = _build_message(device_registration_token, priority, title, message_data)
        messaging.send(message)
