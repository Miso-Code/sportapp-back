import json
import unittest
from unittest.mock import patch

from faker import Faker

from app.models.mappers.data_mapper import DataClassMapper
from app.models.model import UserAlertDevice
from app.models.schemas.schema import UserAlertDeviceCreate
from app.routes import alerts_routes

fake = Faker()


class TestAlertsRoutes(unittest.IsolatedAsyncioTestCase):

    @patch("app.services.alerts.AlertsService.register_device")
    async def test_register_device(self, mock_register_device):
        device = UserAlertDevice(user_id=fake.uuid4(), device_token=fake.uuid4(), enabled=True)
        mock_register_device.return_value = DataClassMapper.to_dict(device)
        response = await alerts_routes.register_device(user_device=UserAlertDeviceCreate(device_token=fake.uuid4()), user_id=fake.uuid4(), db=fake.pystr())
        response_body = json.loads(response.body)

        self.assertEqual(response.status_code, 201)
        self.assertEqual(response_body["user_id"], str(device.user_id))
        self.assertEqual(response_body["device_token"], device.device_token)
        self.assertTrue(response_body["enabled"])

    @patch("app.services.alerts.AlertsService.disable_device")
    async def test_disable_device(self, mock_disable_device):
        device = UserAlertDevice(user_id=fake.uuid4(), device_token=fake.uuid4(), enabled=False)
        mock_disable_device.return_value = DataClassMapper.to_dict(device)
        response = await alerts_routes.disable_device(user_id=fake.uuid4(), db=fake.pystr())
        response_body = json.loads(response.body)

        self.assertEqual(response.status_code, 200)
        self.assertEqual(response_body["user_id"], str(device.user_id))
        self.assertEqual(response_body["device_token"], device.device_token)
        self.assertFalse(response_body["enabled"])

    @patch("app.services.alerts.AlertsService.get_user_device")
    async def test_get_user_device(self, mock_get_user_device):
        device = UserAlertDevice(user_id=fake.uuid4(), device_token=fake.uuid4(), enabled=True)
        mock_get_user_device.return_value = DataClassMapper.to_dict(device)
        response = await alerts_routes.get_user_device(user_id=fake.uuid4(), db=fake.pystr())
        response_body = json.loads(response.body)

        self.assertEqual(response.status_code, 200)
        self.assertEqual(response_body["user_id"], str(device.user_id))
        self.assertEqual(response_body["device_token"], device.device_token)
        self.assertTrue(response_body["enabled"])

    @patch("app.services.alerts.AlertsService.send_test_alert")
    async def test_send_test_alert(self, mock_send_test_alert):
        alert = {"device_token": fake.uuid4(), "priority": "high", "title": fake.sentence(), "message": fake.sentence()}

        mock_return = {"message": "Test alert sent", "alert": alert}
        mock_send_test_alert.return_value = mock_return
        response = await alerts_routes.send_test_alert(fake.uuid4(), message_data=alert, db=fake.pystr())
        response_body = json.loads(response.body)

        self.assertEqual(response.status_code, 200)
        self.assertEqual(response_body["alert"], alert)
        self.assertEqual(response_body["message"], "Test alert sent")
