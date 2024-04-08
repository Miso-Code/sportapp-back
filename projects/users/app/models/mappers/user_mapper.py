import enum
from dataclasses import asdict
from uuid import UUID

from app.models.schemas.profiles_schema import UserPersonalProfile


class DataClassMapper:
    @staticmethod
    def to_dict(instance):
        def custom_encoder(obj):
            if isinstance(obj, UUID):
                return str(obj)
            if isinstance(obj, enum.Enum):
                return obj.value
            return obj

        return {k: custom_encoder(v) for k, v in asdict(instance).items() if v is not None and k != "hashed_password"}

    @staticmethod
    def to_subclass_dict(user, subclass):
        instance = subclass(*[getattr(user, field) for field in subclass.__dataclass_fields__])
        return DataClassMapper.to_dict(instance)
