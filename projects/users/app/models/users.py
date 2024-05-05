import enum
from dataclasses import dataclass
from datetime import datetime
from typing import Literal
from uuid import uuid4, UUID

from sqlalchemy import Column, Uuid, Enum, String, Integer, Float, ForeignKey, DateTime
from sqlalchemy.orm import relationship

from app.config.db import base


class FoodPreference(enum.Enum):
    VEGETARIAN = "vegetarian"
    VEGAN = "vegan"
    EVERYTHING = "everything"


class Gender(enum.Enum):
    MALE = "M"
    FEMALE = "F"
    OTHER = "O"
    PREFER_NOT_TO_SAY = "P"


class TrainingObjective(enum.Enum):
    BUILD_MUSCLE_MASS = "build_muscle_mass"
    LOSE_WEIGHT = "lose_weight"
    TONE_UP = "tone_up"
    MAINTAIN_FITNESS = "maintain_fitness"


class UserIdentificationType(enum.Enum):
    CEDULA_CIUDADANIA = "CC"
    CEDULA_EXTRANJERIA = "CE"
    PASAPORTE = "PA"
    TARJETA_IDENTIDAD = "TI"


class UserSubscriptionType(enum.Enum):
    FREE = "free"
    INTERMEDIATE = "intermediate"
    PREMIUM = "premium"


class PremiumAppointmentType(enum.Enum):
    VIRTUAL = "virtual"
    IN_PERSON = "in_person"


@dataclass
class Trainer(base):
    __tablename__ = "trainers"
    trainer_id: UUID = Column(Uuid(as_uuid=True), primary_key=True, default=uuid4)
    first_name: str = Column(String, nullable=False)
    last_name: str = Column(String, nullable=False)


@dataclass
class UserSportsmanAppointment(base):
    __tablename__ = "user_sportsman_appointments"
    appointment_id: UUID = Column(Uuid(as_uuid=True), primary_key=True, default=uuid4)
    user_id: UUID = Column(Uuid(as_uuid=True), nullable=False)
    appointment_date: datetime = Column(DateTime, nullable=False)
    appointment_type: PremiumAppointmentType = Column(Enum(PremiumAppointmentType), nullable=False)
    appointment_location: str = Column(String, nullable=True)
    trainer_id: UUID = Column(Uuid(as_uuid=True), nullable=False)
    appointment_reason: str = Column(String, nullable=False)


@dataclass
class TrainingLimitation(base):
    __tablename__ = "training_limitations"
    limitation_id: UUID = Column(Uuid(as_uuid=True), primary_key=True, default=uuid4)
    name: str = Column(String, nullable=False)
    description: str = Column(String, nullable=False)


@dataclass
class UserTrainingLimitation(base):
    __tablename__ = "user_training_limitations"
    id: UUID = Column(Uuid(as_uuid=True), primary_key=True, default=uuid4)
    user_id: str = Column(Uuid(as_uuid=True), ForeignKey("users.user_id"))
    limitation_id: str = Column(Uuid(as_uuid=True), ForeignKey("training_limitations.limitation_id"))


@dataclass
class NutritionalLimitation(base):
    __tablename__ = "nutritional_limitations"
    limitation_id: UUID = Column(Uuid(as_uuid=True), primary_key=True, default=uuid4)
    name: str = Column(String, nullable=False)
    description: str = Column(String, nullable=False)


@dataclass
class UserNutritionalLimitation(base):
    __tablename__ = "user_nutritional_limitations"
    id: UUID = Column(Uuid(as_uuid=True), primary_key=True, default=uuid4)
    user_id: str = Column(Uuid(as_uuid=True), ForeignKey("users.user_id"))
    limitation_id: str = Column(Uuid(as_uuid=True), ForeignKey("nutritional_limitations.limitation_id"))


WeekDay = Literal["monday"] | Literal["tuesday"] | Literal["wednesday"] | Literal["thursday"] | Literal["friday"] | Literal["saturday"] | Literal["sunday"]


@dataclass
class User(base):
    __tablename__ = "users"
    # Basic info
    user_id: UUID = Column(Uuid(as_uuid=True), primary_key=True, default=uuid4)
    first_name: str = Column(String, nullable=False)
    last_name: str = Column(String, nullable=False)
    email: str = Column(String, nullable=False, unique=True)
    hashed_password: str = Column(String, nullable=False)
    # Additional info
    identification_type: str = Column(Enum(UserIdentificationType))
    identification_number: str = Column(String)
    gender: str = Column(Enum(Gender))
    country_of_birth: str = Column(String)
    city_of_birth: str = Column(String)
    country_of_residence: str = Column(String)
    city_of_residence: str = Column(String)
    residence_age: int = Column(Integer)
    birth_date: datetime = Column(DateTime)
    # Sport profile
    favourite_sport_id = Column(String)
    training_objective = Column(Enum(TrainingObjective))
    weight: float = Column(Float)
    height: float = Column(Float)
    available_weekdays: str = Column(String, default="")
    preferred_training_start_time: str = Column(String)
    available_training_hours: int = Column(Integer)
    training_limitations = relationship("TrainingLimitation", secondary="user_training_limitations")
    # Additional sport info
    training_years: int = Column(Integer)
    # Nutrition profile
    food_preference: str = Column(Enum(FoodPreference))
    nutritional_limitations = relationship("NutritionalLimitation", secondary="user_nutritional_limitations")
    # Subscription info
    subscription_type: UserSubscriptionType = Column(Enum(UserSubscriptionType), default=UserSubscriptionType.FREE)
    subscription_start_date: datetime = Column(DateTime, nullable=True)
    subscription_end_date: datetime = Column(DateTime, nullable=True)
