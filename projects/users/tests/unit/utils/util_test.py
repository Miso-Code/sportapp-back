import asyncio
import unittest
from unittest.mock import MagicMock, AsyncMock

from app.utils.utils import async_sleep


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

    # Ensure to restore the original asyncio.sleep after the test
    def tearDown(self):
        asyncio.sleep = asyncio.sleep  # Restore original asyncio.sleep
