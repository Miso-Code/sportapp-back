import enum
from uuid import UUID

import sqlalchemy


class DataClassMapper:
    @staticmethod
    def to_dict(instance):
        def custom_encoder(obj):
            if isinstance(obj, UUID):
                return str(obj)
            if isinstance(obj, enum.Enum):
                return obj.value
            return obj

        if isinstance(instance, sqlalchemy.engine.row.Row):
            return {k: custom_encoder(v) for k, v in instance._asdict().items() if v is not None}
        else:
            return {k: custom_encoder(v) for k, v in instance.dict().items() if v is not None}
