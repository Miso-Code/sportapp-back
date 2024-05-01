from dataclasses import dataclass
from datetime import datetime
from uuid import uuid4, UUID

from sqlalchemy import Column, Uuid, Float, DateTime, String, Integer

from app.config.db import base


@dataclass
class SportEvent(base):
    __tablename__ = "sport_events"

    event_id: UUID = Column(Uuid(as_uuid=True), primary_key=True, index=True, default=uuid4)
    sport_id: UUID = Column(Uuid, nullable=False)
    location_latitude: float = Column(Float, nullable=False)
    location_longitude: float = Column(Float, nullable=False)
    start_date: datetime = Column(DateTime, nullable=False)
    end_date: datetime = Column(DateTime, nullable=False)
    title: str = Column(String, nullable=False)
    capacity: int = Column(Integer, nullable=False)
    description: str = Column(String, nullable=False)
