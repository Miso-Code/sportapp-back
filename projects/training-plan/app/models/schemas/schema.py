import enum
from typing import Optional, Literal
from uuid import UUID

from pydantic import BaseModel, confloat, conset, constr

from app.config.settings import Config


class TrainingObjective(enum.Enum):
    BUILD_MUSCLE_MASS = "build_muscle_mass"
    LOSE_WEIGHT = "lose_weight"
    TONE_UP = "tone_up"
    MAINTAIN_FITNESS = "maintain_fitness"


class TrainingLimitation(BaseModel):
    limitation_id: Optional[UUID] = None
    name: str
    description: str


WeekDay = Literal["monday"] | Literal["tuesday"] | Literal["wednesday"] | Literal["thursday"] | Literal["friday"] | Literal["saturday"] | Literal["sunday"]


class TrainingPlanCreate(BaseModel):
    training_objective: TrainingObjective
    available_training_hours: confloat(gt=0)
    available_weekdays: conset(item_type=WeekDay, min_length=1)
    preferred_training_start_time: constr(pattern=Config.HOUR_REGEX)
    favourite_sport_id: Optional[UUID] = None
    weight: Optional[confloat(gt=0)] = None
    height: Optional[confloat(gt=0)] = None
    training_limitations: Optional[list[TrainingLimitation]] = []
