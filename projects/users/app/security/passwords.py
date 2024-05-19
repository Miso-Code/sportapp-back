import hashlib


class PasswordManager:
    @staticmethod
    def get_password_hash(password: str) -> str:
        password_bytes = password.encode()
        sha256 = hashlib.sha256()
        sha256.update(password_bytes)
        hashed_password = sha256.hexdigest()
        return hashed_password

    @staticmethod
    def verify_password(password: str, hashed_password: str) -> bool:
        provided_hash = PasswordManager.get_password_hash(password)
        return provided_hash == hashed_password
