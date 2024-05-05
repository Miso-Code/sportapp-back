import enum
from dataclasses import dataclass
from uuid import UUID, uuid4

from sqlalchemy import Column, Uuid, Float, Enum, String

from app.config.db import base


class WeekDay(enum.Enum):
    MONDAY = "monday"
    TUESDAY = "tuesday"
    WEDNESDAY = "wednesday"
    THURSDAY = "thursday"
    FRIDAY = "friday"
    SATURDAY = "saturday"
    SUNDAY = "sunday"


class FoodCategory(enum.Enum):
    BREAKFAST = "breakfast"
    LUNCH = "lunch"
    DINNER = "dinner"
    SNACK = "snack"
    RECOVERY_SNACK = "recovery_snack"


class FoodTrainingObjective(enum.Enum):
    BUILD_MUSCLE_MASS = "build_muscle_mass"
    LOSE_WEIGHT = "lose_weight"
    TONE_UP = "tone_up"
    MAINTAIN_FITNESS = "maintain_fitness"


class FoodType(enum.Enum):
    VEGAN = "vegan"
    VEGETARIAN = "vegetarian"
    EVERYTHING = "everything"


@dataclass
class FoodIntake(base):
    __tablename__ = "food_intakes"

    food_intake_id: UUID = Column(Uuid(as_uuid=True), primary_key=True, default=uuid4)
    user_id: UUID = Column(Uuid(as_uuid=True), nullable=False)
    week_day: WeekDay = Column(Enum(WeekDay), nullable=False)
    dish_id: UUID = Column(Uuid(as_uuid=True), nullable=False)


# 1500


@dataclass
class Dish(base):
    __tablename__ = "dishes"

    dish_id: UUID = Column(Uuid(as_uuid=True), primary_key=True, nullable=False, default=uuid4)
    name: str = Column(String, nullable=False)
    name_es: str = Column(String, nullable=False)
    category: FoodCategory = Column(Enum(FoodCategory), primary_key=True, nullable=False)
    calories: float = Column(Float, nullable=False)
    carbs: float = Column(Float, nullable=False)
    protein: float = Column(Float, nullable=False)
    fat: float = Column(Float, nullable=False)
    objective: FoodTrainingObjective = Column(Enum(FoodTrainingObjective), nullable=False)
    food_type: FoodType = Column(Enum(FoodType), nullable=False)
