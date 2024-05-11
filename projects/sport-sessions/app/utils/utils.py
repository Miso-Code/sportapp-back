from fastapi import Header

from app.config.settings import Config
from app.exceptions.exceptions import InvalidApiKeyError


def validate_api_key(x_api_key: str = Header(None)):
    if x_api_key is None or x_api_key != Config.SPORT_SESSIONS_API_KEY:
        raise InvalidApiKeyError("Invalid API key")
    return x_api_key
