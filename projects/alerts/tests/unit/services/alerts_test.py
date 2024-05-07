import unittest
from unittest.mock import MagicMock, patch

from faker import Faker
from sqlalchemy.orm import Session

from app.exceptions.exceptions import NotFoundError
from app.models.model import UserAlertDevice
from app.models.schemas.schema import UserAlertDeviceCreate, TestAlert
from app.services.alerts import AlertsService

fake = Faker()


class TestAlertsService(unittest.TestCase):
    def setUp(self):
        self.mock_db = MagicMock(spec=Session)
        self.alerts_service = AlertsService(self.mock_db)

    def test_register_device(self):
        user_id = fake.uuid4()
        device_token = fake.uuid4()
        alert_data = UserAlertDeviceCreate(device_token=device_token)

        self.mock_db.query().filter().first.return_value = None
        response = self.alerts_service.register_device(user_id, alert_data)

        self.assertEqual(response["user_id"], str(user_id))
        self.assertEqual(response["device_token"], device_token)

    def test_update_device(self):
        user_id = fake.uuid4()
        device_token = fake.uuid4()
        alert_data = UserAlertDeviceCreate(device_token=device_token)
        existing_device = UserAlertDevice(user_id=user_id, device_token=fake.uuid4())

        self.mock_db.query().filter().first.return_value = existing_device

        response = self.alerts_service.register_device(user_id, alert_data)

        self.assertEqual(response["user_id"], str(user_id))
        self.assertEqual(response["device_token"], device_token)

    def test_get_user_device(self):
        user_id = fake.uuid4()
        device_token = fake.uuid4()
        existing_device = UserAlertDevice(user_id=user_id, device_token=device_token)

        self.mock_db.query().filter().first.return_value = existing_device

        response = self.alerts_service.get_user_device(user_id)
        print(response)

        self.assertEqual(response["user_id"], str(user_id))
        self.assertEqual(response["device_token"], device_token)

    def test_get_user_device_not_found(self):
        user_id = fake.uuid4()

        self.mock_db.query().filter().first.return_value = None

        with self.assertRaises(NotFoundError) as context:
            self.alerts_service.get_user_device(user_id)
        self.assertEqual(str(context.exception), f"User {user_id} has no registered devices")

    def test_disable_device(self):
        user_id = fake.uuid4()
        device_token = fake.uuid4()
        existing_device = UserAlertDevice(user_id=user_id, device_token=device_token)

        self.mock_db.query().filter().first.return_value = existing_device

        response = self.alerts_service.disable_device(user_id)

        self.assertEqual(response["user_id"], str(user_id))
        self.assertEqual(response["device_token"], device_token)
        self.assertFalse(response["enabled"])

    def test_disable_device_not_found(self):
        user_id = fake.uuid4()

        self.mock_db.query().filter().first.return_value = None

        with self.assertRaises(NotFoundError) as context:
            self.alerts_service.disable_device(user_id)
        self.assertEqual(str(context.exception), f"User {user_id} has no registered devices")

    @patch("app.firebase.firebase.FirebaseClient.send_fcm_alert")
    def test_send_test_alert(self, mock_send_fcm_alert):
        device_token = fake.uuid4()

        alert_data = TestAlert(device_token=device_token, priority="high", title=fake.word(), message=fake.sentence())

        mock_send_fcm_alert.return_value = None

        response = self.alerts_service.send_test_alert(alert_data)

        self.assertEqual(response["message"], "Test alert sent")
        self.assertEqual(response["alert"], alert_data.dict())
        mock_send_fcm_alert.assert_called_once_with(alert_data.device_token, alert_data.priority, alert_data.title, alert_data.message)
