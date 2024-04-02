import bcrypt
from sqlalchemy.orm import Session

from ..jwt.generator import JWTGenerator
from ..models.users import User
from ..models.mappers.mapper import DataClassMapper
from ..exceptions.exceptions import NotFoundError


def _get_password_hash(password):
    pwd_bytes = password.encode("utf-8")
    salt = bcrypt.gensalt()
    hashed_password = bcrypt.hashpw(password=pwd_bytes, salt=salt)
    return hashed_password


def _verify_password(plain_password, hashed_password):
    password_byte_enc = plain_password.encode("utf-8")
    return bcrypt.checkpw(password=password_byte_enc, hashed_password=hashed_password)


def _create_user_object(user_create):
    user = User()
    user.email = user_create.email
    user.first_name = user_create.first_name
    user.last_name = user_create.last_name
    user.hashed_password = _get_password_hash(user_create.password)
    return user


class UsersService:
    def __init__(self, db: Session):
        self.db = db
        self.mapper = DataClassMapper(User)
        self.jwt = JWTGenerator()

    def create_users(self, users_create):
        users = [_create_user_object(user_create) for user_create in users_create]
        self.db.bulk_save_objects(users)
        self.db.commit()

    def complete_user_registration(self, user_id, user_additional_information):
        user = self.db.query(User).filter(User.user_id == user_id).first()
        if not user:
            raise NotFoundError(f"User with id {user_id} not found")

        user.identification_type = user_additional_information.identification_type
        user.identification_number = user_additional_information.identification_number
        user.gender = user_additional_information.gender
        user.country_of_birth = user_additional_information.country_of_birth
        user.city_of_birth = user_additional_information.city_of_birth
        user.country_of_residence = user_additional_information.country_of_residence
        user.city_of_residence = user_additional_information.city_of_residence
        user.residence_age = user_additional_information.residence_age
        user.birth_date = user_additional_information.birth_date

        self.db.commit()

        return self.mapper.to_dict(user)
