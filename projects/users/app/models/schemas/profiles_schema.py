from dataclasses import dataclass

from app.models.users import UserIdentificationType, Gender


@dataclass
class UserPersonalProfile:
    email: str
    first_name: str
    last_name: str
    identification_type: UserIdentificationType
    identification_number: str
    gender: Gender
    country_of_birth: str
    city_of_birth: str
    country_of_residence: str
    city_of_residence: str
    residence_age: int
    birth_date: str
