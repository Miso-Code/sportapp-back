from datetime import datetime
from typing import List
from uuid import uuid4

from sqlalchemy import Column, Uuid, Integer, Float, ForeignKey, Boolean, DateTime
from sqlalchemy.orm import relationship, Mapped
from ..config.db import base


class SportSession(base):
    __tablename__ = "sport_sessions"
    session_id = Column(Uuid(as_uuid=True), primary_key=True, default=uuid4)
    user_id = Column(Uuid(as_uuid=True), nullable=False)
    sport_id = Column(Uuid(as_uuid=True), nullable=False)
    duration = Column(Integer, nullable=True)
    steps = Column(Integer, nullable=True)
    distance = Column(Integer, nullable=True)
    calories = Column(Integer, nullable=True)
    average_speed = Column(Integer, nullable=True)
    locations: Mapped[List["Location"]] = relationship("Location", back_populates="sport_session")
    min_heartrate = Column(Integer, nullable=True)
    max_heartrate = Column(Integer, nullable=True)
    avg_heartrate = Column(Integer, nullable=True)
    is_active = Column(Boolean, nullable=False, default=True)
    started_at = Column(DateTime, nullable=False, default=datetime.now())


class Location(base):
    __tablename__ = "sport_session_locations"
    location_id = Column(Uuid(as_uuid=True), primary_key=True, default=uuid4)
    session_id = Column(Uuid(as_uuid=True), ForeignKey("sport_sessions.session_id"))
    sport_session: Mapped["SportSession"] = relationship("SportSession", back_populates="locations")
    latitude = Column(Float, nullable=False)
    longitude = Column(Float, nullable=False)
    accuracy = Column(Float, nullable=True)
    altitude = Column(Float, nullable=True)
    altitude_accuracy = Column(Float, nullable=True)
    heading = Column(Float, nullable=True)
    speed = Column(Float, nullable=True)
    created_at = Column(DateTime, nullable=False, default=datetime.now())
