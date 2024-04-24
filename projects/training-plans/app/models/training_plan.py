from dataclasses import dataclass
from uuid import uuid4, UUID

from sqlalchemy import Column, Uuid, String, Float

from app.config.db import base
from app.models.schemas.schema import WeekDay


@dataclass
class TrainingPlanSession(base):
    __tablename__ = "training_plan_sessions"
    training_plan_session_id: UUID = Column(Uuid(as_uuid=True), primary_key=True, default=uuid4)
    weekday: WeekDay = Column(String)
    start_time: str = Column(String, nullable=False)
    warm_up: float = Column(Float)
    cardio: float = Column(Float)
    strength: float = Column(Float)
    cool_down: float = Column(Float)
    user_id: UUID = Column(Uuid(as_uuid=True), nullable=False)
