from dataclasses import asdict
from datetime import datetime
from uuid import UUID


class DataClassMapper:
    @staticmethod
    def to_dict(instance):
        def custom_encoder(obj):
            if isinstance(obj, UUID):
                return str(obj)
            return obj

        return {k: custom_encoder(v) for k, v in asdict(instance).items() if v is not None}
