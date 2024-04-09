import asyncio
import math


async def async_sleep(seconds):
    if seconds < 0:
        raise ValueError("Sleep duration cannot be negative")
    return await asyncio.sleep(seconds)


def calculate_bmi(weight, height):
    if height == 0:
        return 0
    return round(weight / (math.pow(height, 2)), 2)
