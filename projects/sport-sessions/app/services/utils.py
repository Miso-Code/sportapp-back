import math
from typing import List

from app.config.settings import Config
from app.models.model import Location


def _haversine(lat1, lon1, lat2, lon2):
    R = 6371  # radius of Earth in kilometers
    phi1 = math.radians(lat1)
    phi2 = math.radians(lat2)
    delta_phi = math.radians(lat2 - lat1)
    delta_lambda = math.radians(lon2 - lon1)
    a = math.sin(delta_phi / 2) ** 2 + math.cos(phi1) * math.cos(phi2) * math.sin(delta_lambda / 2) ** 2
    res = R * (2 * math.atan2(math.sqrt(a), math.sqrt(1 - a)))
    return res


def _calculate_total_distance_coordinates(locations):
    total_distance = 0
    for i in range(1, len(locations)):
        lat1, lon1 = locations[i - 1]
        lat2, lon2 = locations[i]
        total_distance += _haversine(lat1, lon1, lat2, lon2)
    return total_distance


def estimate_distance(steps: int, locations: List[Location] = []):
    if not locations:
        return steps * Config.AVG_STEP_LENGTH
    else:
        locations = [(location.latitude, location.longitude) for location in locations]
        return _calculate_total_distance_coordinates(locations)


def estimate_calories_burned(steps: int):
    # TODO: Change this to a more accurate formula like the Metabolic Equivalent of Task
    return steps * Config.AVG_CALORIES_PER_STEP


def estimate_speed(distance=0, duration=0, locations: List[Location] = []):
    if locations:
        speed_accumulator = 0
        for location in locations:
            speed_accumulator += location.speed

        return speed_accumulator / len(locations)

    elif distance and duration:
        return distance / duration
    return None
