from typing import List, Dict
from app.models.schemas.schema import UserCreate


class UserCache:
    users: List[UserCreate] = []  # List of users to be synchronized
    users_with_errors_by_email_map: Dict[str, UserCreate] = {}  # Map of users with errors by email (duplicate email)
    users_success_by_email_map: Dict[str, UserCreate] = {}  # Map of successfully created users by email
