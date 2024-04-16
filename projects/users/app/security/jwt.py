from datetime import datetime, timedelta, timezone
from typing import Dict

from jose import jwt, JWTError
from app.exceptions.exceptions import InvalidCredentialsError
from app.security.passwords import PasswordManager
from app.utils import utils

INVALID_EXPIRED_MESSAGE = "Invalid or expired refresh token"


class JWTManager:
    def __init__(self, secret_key: str, algorithm: str, access_token_expiry_minutes: int, refresh_token_expiry_minutes: int):
        self._secret = secret_key
        self._algorithm = algorithm
        self._access_token_expiry = access_token_expiry_minutes
        self._refresh_token_expiry = refresh_token_expiry_minutes

    def process_refresh_token_login(self, refresh_token):
        try:
            return self.refresh_token(refresh_token)
        except JWTError:
            raise InvalidCredentialsError("Invalid or expired refresh token")

    def process_email_password_login(self, user_id, input_password, user_password, user_subscription_type):
        if not PasswordManager.verify_password(input_password, user_password):
            raise InvalidCredentialsError("Invalid email or password")

        scopes = utils.get_user_scopes(user_subscription_type)
        return self.generate_tokens(str(user_id), scopes)

    def generate_tokens(self, user_id, scopes) -> Dict[str, str]:
        payload = {"user_id": user_id, "scopes": scopes}
        return {
            "user_id": user_id,
            "access_token": self._create_token(payload, self._access_token_expiry),
            "access_token_expires_minutes": self._access_token_expiry,
            "refresh_token": self._create_token(payload, self._refresh_token_expiry),
            "refresh_token_expires_minutes": self._refresh_token_expiry,
        }

    def refresh_token(self, token: str) -> Dict[str, str]:
        try:
            payload = self._decode_token(token)
        except JWTError:
            raise InvalidCredentialsError(INVALID_EXPIRED_MESSAGE)
        if not payload or "expiry" not in payload:
            raise InvalidCredentialsError(INVALID_EXPIRED_MESSAGE)

        if datetime.now(timezone.utc).timestamp() > payload["expiry"]:
            raise InvalidCredentialsError(INVALID_EXPIRED_MESSAGE)

        return self.generate_tokens(payload["user_id"], payload["scopes"])

    def _create_token(self, payload: Dict, expires_in_minutes: int) -> str:
        expiration_time = datetime.now(timezone.utc) + timedelta(minutes=expires_in_minutes)
        payload_with_exp = {**payload, "expiry": expiration_time.timestamp()}
        return jwt.encode(payload_with_exp, self._secret, self._algorithm)

    def _decode_token(self, token: str) -> Dict:
        return jwt.decode(token, self._secret, self._algorithm)
