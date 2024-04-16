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


def get_user_scopes(subscription_type):
    scopes = []
    if subscription_type == "free":
        scopes.append("free")
    elif subscription_type == "intermediate":
        scopes.append("free")
        scopes.append("intermediate")
    elif subscription_type == "premium":
        scopes.append("free")
        scopes.append("intermediate")
        scopes.append("premium")
    elif subscription_type == "business_partner":
        scopes.append("business_partner")
    return scopes
