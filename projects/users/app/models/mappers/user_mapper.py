import enum
from dataclasses import asdict
from uuid import UUID

from app.models.schemas.profiles_schema import UserPersonalProfile, UserNutritionalProfile, UserSportsProfileGet
from app.utils import utils


class DataClassMapper:
    @staticmethod
    def to_dict(instance, pydantic=False):
        def custom_encoder(obj):
            if isinstance(obj, UUID):
                return str(obj)
            if isinstance(obj, enum.Enum):
                return obj.value
            if isinstance(obj, set):
                return list(obj)
            return obj

        if pydantic:
            return {k: custom_encoder(v) for k, v in instance.dict().items() if v is not None and k != "hashed_password"}
        else:
            return {k: custom_encoder(v) for k, v in asdict(instance).items() if v is not None and k != "hashed_password"}

    @staticmethod
    def to_user_nutritional_profile(user):
        user_nutritional_profile = UserNutritionalProfile(food_preference=user.food_preference, nutritional_limitations=[])

        user_nutritional_profile_dict = DataClassMapper.to_dict(user_nutritional_profile, pydantic=True)
        user_nutritional_profile_dict["nutritional_limitations"] = [str(limitation.limitation_id) for limitation in user.nutritional_limitations]
        return user_nutritional_profile_dict

    @staticmethod
    def to_user_personal_profile(user):
        user_personal_profile = UserPersonalProfile(
            email=user.email,
            first_name=user.first_name,
            last_name=user.last_name,
            identification_type=user.identification_type,
            identification_number=user.identification_number,
            gender=user.gender,
            country_of_birth=user.country_of_birth,
            city_of_birth=user.city_of_birth,
            country_of_residence=user.country_of_residence,
            city_of_residence=user.city_of_residence,
            residence_age=user.residence_age,
            birth_date=user.birth_date,
        )

        return DataClassMapper.to_dict(user_personal_profile, pydantic=True)

    @staticmethod
    def to_user_sports_profile(user):
        user_sports_profile = UserSportsProfileGet(
            favourite_sport_id=user.favourite_sport_id,
            training_objective=user.training_objective,
            weight=user.weight,
            height=user.height,
            available_training_hours=user.available_training_hours,
            available_weekdays=user.available_weekdays.split(","),
            preferred_training_start_time=user.preferred_training_start_time,
            training_limitations=[DataClassMapper.to_dict(limitation) for limitation in user.training_limitations],
        )

        user_sports_profile_dict = DataClassMapper.to_dict(user_sports_profile, pydantic=True)

        if "weight" in user_sports_profile_dict and "height" in user_sports_profile_dict:
            user_sports_profile_dict["bmi"] = utils.calculate_bmi(user_sports_profile_dict["weight"], user_sports_profile_dict["height"])
        return user_sports_profile_dict

    @staticmethod
    def to_training_plan_create(user):
        return {
            "training_objective": user.training_objective.value,
            "available_training_hours": user.available_training_hours,
            "available_weekdays": user.available_weekdays.split(","),
            "preferred_training_start_time": user.preferred_training_start_time,
            "favourite_sport_id": user.favourite_sport_id,
            "weight": user.weight,
            "height": user.height,
            "training_limitations": [DataClassMapper.to_dict(limitation) for limitation in user.training_limitations],
        }
