from datetime import datetime, timedelta, timezone
from typing import Dict

from jose import jwt, JWTError
from app.exceptions.exceptions import InvalidCredentialsError


class JWTManager:
    def __init__(self, secret_key: str, algorithm: str, access_token_expiry_minutes: int, refresh_token_expiry_minutes: int):
        self._secret = secret_key
        self._algorithm = algorithm
        self._access_token_expiry = access_token_expiry_minutes
        self._refresh_token_expiry = refresh_token_expiry_minutes

    def generate_tokens(self, payload: Dict) -> Dict[str, str]:
        return {
            "access_token": self._create_token(payload, self._access_token_expiry),
            "access_token_expires_minutes": self._access_token_expiry,
            "refresh_token": self._create_token(payload, self._refresh_token_expiry),
            "refresh_token_expires_minutes": self._refresh_token_expiry,
        }

    def refresh_token(self, token: str) -> Dict[str, str]:
        try:
            payload = self._decode_token(token)
        except JWTError:
            raise InvalidCredentialsError("Invalid or expired refresh token")
        if not payload or "expiry" not in payload:
            raise InvalidCredentialsError("Invalid or expired refresh token")

        if datetime.now(timezone.utc).timestamp() > payload["expiry"]:
            raise InvalidCredentialsError("Invalid or expired refresh token")

        return self.generate_tokens(payload)

    def _create_token(self, payload: Dict, expires_in_minutes: int) -> str:
        expiration_time = datetime.now(timezone.utc) + timedelta(minutes=expires_in_minutes)
        payload_with_exp = {**payload, "expiry": expiration_time.timestamp()}
        return jwt.encode(payload_with_exp, self._secret, self._algorithm)

    def _decode_token(self, token: str) -> Dict:
        return jwt.decode(token, self._secret, self._algorithm)
