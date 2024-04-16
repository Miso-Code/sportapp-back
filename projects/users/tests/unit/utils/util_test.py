import asyncio
import unittest
from unittest.mock import AsyncMock

from faker import Faker

from app.utils.utils import async_sleep, calculate_bmi, get_user_scopes

fake = Faker()


class TestAsyncSleep(unittest.IsolatedAsyncioTestCase):
    async def test_sleep_duration(self):
        duration = 1  # seconds
        start_time = asyncio.get_running_loop().time()
        await async_sleep(duration)
        end_time = asyncio.get_running_loop().time()
        elapsed_time = end_time - start_time
        self.assertAlmostEqual(elapsed_time, duration, delta=0.2)  # Slightly larger delta

    async def test_negative_input(self):
        with self.assertRaises(ValueError):
            await async_sleep(-1)

    async def test_zero_input(self):
        await async_sleep(0)

    async def test_multiple_calls(self):
        duration = 0.5  # seconds
        start_time = asyncio.get_running_loop().time()
        await asyncio.gather(async_sleep(duration), async_sleep(duration), async_sleep(duration))
        end_time = asyncio.get_running_loop().time()
        elapsed_time = end_time - start_time
        expected_duration = duration  # All calls should take approximately the same time
        self.assertAlmostEqual(elapsed_time, expected_duration, delta=0.1)


class TestMockSleep(unittest.IsolatedAsyncioTestCase):
    async def test_mock_sleep(self):
        duration = 1  # seconds
        mocked_sleep = AsyncMock()
        asyncio.sleep = mocked_sleep
        await async_sleep(duration)
        mocked_sleep.assert_called_once_with(duration)


class TestCalculateBmi(unittest.TestCase):
    def test_calculate_bmi(self):
        height = fake.random_int(150, 200) / 100
        weight = fake.random_int(40, 120)
        expected_bmi = round(weight / (height**2), 2)
        actual_bmi = calculate_bmi(weight, height)
        self.assertEqual(expected_bmi, actual_bmi)

    def test_calculate_bmi_zero_height(self):
        height = 0
        weight = fake.random_int(40, 120)
        bmi = calculate_bmi(weight, height)
        self.assertEqual(bmi, 0)


class TestGetUserScopes(unittest.TestCase):
    def test_get_user_scopes_free(self):
        subscription_type = "free"
        expected_scopes = ["free"]
        actual_scopes = get_user_scopes(subscription_type)
        self.assertListEqual(expected_scopes, actual_scopes)

    def test_get_user_scopes_intermediate(self):
        subscription_type = "intermediate"
        expected_scopes = ["free", "intermediate"]
        actual_scopes = get_user_scopes(subscription_type)
        self.assertListEqual(expected_scopes, actual_scopes)

    def test_get_user_scopes_premium(self):
        subscription_type = "premium"
        expected_scopes = ["free", "intermediate", "premium"]
        actual_scopes = get_user_scopes(subscription_type)
        self.assertListEqual(expected_scopes, actual_scopes)

    def test_get_user_scopes_business_partner(self):
        subscription_type = "business_partner"
        expected_scopes = ["business_partner"]
        actual_scopes = get_user_scopes(subscription_type)
        self.assertListEqual(expected_scopes, actual_scopes)
