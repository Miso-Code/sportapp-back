import enum
from dataclasses import asdict
from uuid import UUID


class DataClassMapper:
    def __init__(self, data_class):
        self.data_class = data_class

    def to_dict(self, instance):
        def custom_encoder(obj):
            if isinstance(obj, UUID):
                return str(obj)
            if isinstance(obj, enum.Enum):
                return obj.value
            return obj

        return {k: custom_encoder(v) for k, v in asdict(instance).items() if v is not None}
