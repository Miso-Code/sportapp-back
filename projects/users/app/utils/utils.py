import asyncio
import math
from datetime import datetime


async def async_sleep(seconds):
    if seconds < 0:
        raise ValueError("Sleep duration cannot be negative")
    return await asyncio.sleep(seconds)


def calculate_bmi(weight, height):
    if height == 0:
        return 0
    return round(weight / (math.pow(height, 2)), 2)


def get_user_scopes(subscription_type):
    scopes = ["free"]
    if subscription_type == "intermediate":
        scopes.append("intermediate")
    elif subscription_type == "premium":
        scopes.append("intermediate")
        scopes.append("premium")
    return scopes


def calculate_age(birth_date: datetime):
    current_date = datetime.now()
    age = current_date.year - birth_date.year - ((current_date.month, current_date.day) < (birth_date.month, birth_date.day))
    return age
