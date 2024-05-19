from uuid import UUID

from pydantic import BaseModel

from app.models.model import FoodType, FoodTrainingObjective


class CaloricIntakeSQSMessage(BaseModel):
    user_id: UUID
    message: str
    date: str


class SessionCalories(BaseModel):
    calories_burn_expected: float
    calories_burn: float


class NutritionalPlanCreate(BaseModel):
    age: int
    gender: str
    training_objective: FoodTrainingObjective
    weight: float
    height: float
    food_preference: FoodType
    nutritional_limitations: list[str]
