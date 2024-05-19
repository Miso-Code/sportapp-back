from dataclasses import asdict
from datetime import datetime
from uuid import UUID


class DataClassMapper:
    @staticmethod
    def to_dict(instance):
        def custom_encoder(obj):
            if isinstance(obj, UUID):
                return str(obj)
            if isinstance(obj, datetime):
                return obj.isoformat()
            return obj

        return {k: custom_encoder(v) for k, v in asdict(instance).items() if v is not None and k != "hashed_password"}
