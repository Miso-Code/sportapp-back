from datetime import datetime, timedelta, timezone
from typing import Dict
from uuid import UUID

from jose import jwt, JWTError
from app.exceptions.exceptions import InvalidCredentialsError
from app.models.users import UserSubscriptionType
from app.utils import utils

INVALID_EXPIRED_MESSAGE = "Invalid or expired refresh token"


class JWTManager:
    def __init__(self, secret_key: str, algorithm: str, access_token_expiry_minutes: int, refresh_token_expiry_minutes: int):
        self._secret = secret_key
        self._algorithm = algorithm
        self._access_token_expiry = access_token_expiry_minutes
        self._refresh_token_expiry = refresh_token_expiry_minutes

    def generate_tokens(self, user_id: UUID, user_subscription_type: UserSubscriptionType) -> Dict[str, str]:
        scopes = utils.get_user_scopes(user_subscription_type)
        payload = {"user_id": str(user_id), "scopes": scopes}
        return {
            "user_id": str(user_id),
            "access_token": self._create_token(payload, self._access_token_expiry),
            "access_token_expires_minutes": self._access_token_expiry,
            "refresh_token": self._create_token(payload, self._refresh_token_expiry, refresh=True),
            "refresh_token_expires_minutes": self._refresh_token_expiry,
        }

    def decode_refresh_token(self, refresh_token: str) -> str:
        try:
            payload = self._decode_token(refresh_token)
        except JWTError:
            raise InvalidCredentialsError(INVALID_EXPIRED_MESSAGE)
        if not payload or "expiry" not in payload:
            raise InvalidCredentialsError(INVALID_EXPIRED_MESSAGE)
        if "refresh" not in payload:
            raise InvalidCredentialsError("Not a refresh token")
        if datetime.now(timezone.utc).timestamp() > payload["expiry"]:
            raise InvalidCredentialsError(INVALID_EXPIRED_MESSAGE)

        return payload["user_id"]

    def _create_token(self, payload: Dict, expires_in_minutes: int, refresh: bool = False) -> str:
        if refresh:
            payload["refresh"] = True
        expiration_time = datetime.now(timezone.utc) + timedelta(minutes=expires_in_minutes)
        payload_with_exp = {**payload, "expiry": expiration_time.timestamp()}
        return jwt.encode(payload_with_exp, self._secret, self._algorithm)

    def _decode_token(self, token: str) -> Dict:
        return jwt.decode(token, self._secret, self._algorithm)
