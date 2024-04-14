from uuid import UUID

import bcrypt
from jose import JWTError
from sqlalchemy.orm import Session
from sqlalchemy.dialects.postgresql import insert

from app.config.settings import Config
from app.security.jwt import JWTManager
from app.models.users import User, NutritionalLimitation, TrainingLimitation
from app.models.mappers.user_mapper import DataClassMapper
from app.exceptions.exceptions import NotFoundError, InvalidCredentialsError
from app.services.external import ExternalServices
from app.utils import utils


def _get_password_hash(password):
    pwd_bytes = password.encode("utf-8")
    salt = bcrypt.gensalt(rounds=12)
    hashed_password = bcrypt.hashpw(password=pwd_bytes, salt=salt)
    return hashed_password.decode("utf-8")


def _verify_password(password, hashed_password):
    password_bytes = password.encode("utf-8")
    hashed_password_bytes = hashed_password.encode("utf-8")
    return bcrypt.checkpw(password=password_bytes, hashed_password=hashed_password_bytes)


class UsersService:
    def __init__(self, db: Session, user_token: str = None):
        self.user_token = user_token
        self.db = db
        self.jwt_manager = JWTManager(Config.JWT_SECRET_KEY, Config.JWT_ALGORITHM, Config.ACCESS_TOKEN_EXPIRE_MINUTES, Config.REFRESH_TOKEN_EXPIRE_MINUTES)
        self.external_services = ExternalServices()

    def create_users(self, users_create):
        values_to_insert = []
        for user_create in users_create:
            user = user_create.model_dump()
            user["hashed_password"] = _get_password_hash(user["password"])
            del user["password"]
            values_to_insert.append(user)
        if not values_to_insert:
            return []
        insert_statement = insert(User).values(values_to_insert).returning(User.user_id, User.first_name, User.last_name, User.email)
        created_users = self.db.execute(insert_statement).fetchall()
        self.db.commit()
        return [self._create_user_dict(user) for user in created_users]

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

        return DataClassMapper.to_dict(user)

    def authenticate_user(self, user_credentials):
        if user_credentials.refresh_token:
            return self._process_refresh_token_login(user_credentials.refresh_token)
        else:
            return self._process_email_password_login(user_credentials.email, user_credentials.password)

    def get_user_personal_information(self, user_id):
        user = self.get_user_by_id(user_id)
        return DataClassMapper.to_user_personal_profile(user)

    def get_user_sports_information(self, user_id):
        user = self.get_user_by_id(user_id)
        return DataClassMapper.to_user_sports_profile(user)

    def get_user_nutritional_information(self, user_id):
        user = self.get_user_by_id(user_id)
        return DataClassMapper.to_user_nutritional_profile(user)

    # noinspection PyMethodMayBeStatic
    def _create_user_dict(self, user_data):
        return {"user_id": str(user_data[0]), "first_name": user_data[1], "last_name": user_data[2], "email": user_data[3]}

    def _process_email_password_login(self, email, password):
        user = self.db.query(User).filter(User.email == email).first()
        if not user:
            raise InvalidCredentialsError("Invalid email or password")

        if not _verify_password(password, user.hashed_password):
            raise InvalidCredentialsError("Invalid email or password")

        scopes = utils.get_user_scopes(user.subscription_type)

        return self.jwt_manager.generate_tokens(str(user.user_id), scopes)

    def _process_refresh_token_login(self, refresh_token):
        try:
            return self.jwt_manager.refresh_token(refresh_token)
        except JWTError:
            raise InvalidCredentialsError("Invalid or expired refresh token")

    def get_user_by_id(self, user_id):
        user = self.db.query(User).filter(User.user_id == user_id).first()
        if not user:
            raise NotFoundError(f"User with id {user_id} not found")
        return user

    def get_nutritional_limitations(self):
        nutritional_limitations = self.db.query(NutritionalLimitation).all()
        return [DataClassMapper.to_dict(limitation) for limitation in nutritional_limitations]

    def update_user_personal_information(self, user_id, personal_profile):
        user = self.get_user_by_id(user_id)
        for field in personal_profile.dict(exclude_defaults=True).keys():
            setattr(user, field, getattr(personal_profile, field))

        self.db.commit()
        return DataClassMapper.to_user_personal_profile(user)

    def update_user_nutritional_information(self, user_id, nutritional_profile):
        user = self.get_user_by_id(user_id)
        if nutritional_profile.food_preference:
            user.food_preference = nutritional_profile.food_preference

        user.nutritional_limitations = []
        for limitation_id in nutritional_profile.nutritional_limitations:
            limitation = self.db.query(NutritionalLimitation).filter(NutritionalLimitation.limitation_id == UUID(limitation_id)).first()
            if limitation:
                user.nutritional_limitations.append(limitation)
            else:
                raise NotFoundError(f"Nutritional limitation with id {limitation_id} not found")

        self.db.commit()
        return DataClassMapper.to_user_nutritional_profile(user)

    def update_user_sports_information(self, user_id, sports_profile):
        user = self.get_user_by_id(user_id)
        for field in sports_profile.dict(exclude={"favourite_sport_id", "training_limitations"}, exclude_defaults=True).keys():
            setattr(user, field, getattr(sports_profile, field))

        if sports_profile.favourite_sport_id:
            sport = self.external_services.get_sport(sports_profile.favourite_sport_id, self.user_token)
            user.favourite_sport_id = sport["sport_id"]

        user.training_limitations = self._process_training_limitations(sports_profile.training_limitations)
        self.db.commit()
        return DataClassMapper.to_user_sports_profile(user)

    def _process_training_limitations(self, training_limitations_to_update: list[TrainingLimitation]):
        training_limitations = []
        for training_limitation in training_limitations_to_update:
            if training_limitation.limitation_id:
                limitation_id = training_limitation.limitation_id
                limitation = self.db.query(TrainingLimitation).filter(TrainingLimitation.limitation_id == limitation_id).first()
                if limitation:
                    limitation.name = training_limitation.name
                    limitation.description = training_limitation.description
                    training_limitations.append(limitation)
                else:
                    raise NotFoundError(f"Training limitation with id {limitation_id} not found")
            else:
                training_limitations.append(self._create_training_limitation(training_limitation))

        return training_limitations

    def _create_training_limitation(self, training_limitation):
        return TrainingLimitation(name=training_limitation.name, description=training_limitation.description)
