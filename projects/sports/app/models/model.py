import enum
from uuid import uuid4

from sqlalchemy import Column, String, Uuid
from ..config.db import base


class Sport(base):
    __tablename__ = "sports"
    sport_id = Column(Uuid(as_uuid=True), primary_key=True, default=uuid4)
    name = Column(String, nullable=False)
