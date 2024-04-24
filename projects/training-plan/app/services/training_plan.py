import math
from uuid import UUID

from sqlalchemy.orm import Session

from app.models.mappers.training_plan_mapper import DataClassMapper
from app.models.schemas.schema import TrainingPlanCreate, TrainingObjective
from app.models.training_plan import TrainingPlanSession


def _create_session_plan_intensity(session_duration: float, objective: TrainingObjective) -> dict[str, float]:
    if objective == TrainingObjective.LOSE_WEIGHT:
        return {
            "warm_up": session_duration * 0.1,
            "cardio": session_duration * 0.6,
            "cool_down": session_duration * 0.3,
        }
    elif objective == TrainingObjective.TONE_UP:
        return {
            "warm_up": session_duration * 0.2,
            "cardio": session_duration * 0.4,
            "strength": session_duration * 0.3,
            "cool_down": session_duration * 0.1,
        }
    elif objective == TrainingObjective.BUILD_MUSCLE_MASS:
        return {
            "warm_up": session_duration * 0.1,
            "strength": session_duration * 0.7,
            "cool_down": session_duration * 0.2,
        }
    elif objective == TrainingObjective.MAINTAIN_FITNESS:
        return {
            "warm_up": session_duration * 0.2,
            "cardio": session_duration * 0.4,
            "strength": session_duration * 0.2,
            "cool_down": session_duration * 0.2,
        }


class TrainingPlanService:
    def __init__(self, db: Session):
        self.db = db

    def generate_training_plan(self, user_id: UUID, training_plan: TrainingPlanCreate):
        self.db.query(TrainingPlanSession).filter(TrainingPlanSession.user_id == user_id).delete()

        created_sessions = []
        for weekday in training_plan.available_weekdays:
            session_intensity = _create_session_plan_intensity(training_plan.available_training_hours, training_plan.training_objective)
            session = TrainingPlanSession(
                weekday=weekday,
                start_time=training_plan.preferred_training_start_time,
                warm_up=session_intensity.get("warm_up", 0),
                cardio=session_intensity.get("cardio", 0),
                strength=session_intensity.get("strength", 0),
                cool_down=session_intensity.get("cool_down", 0),
                user_id=user_id,
            )
            self.db.add(session)
            created_sessions.append(session)
        self.db.commit()
        response = []
        for session in created_sessions:
            self.db.refresh(session)
            response.append(DataClassMapper.to_dict(session))
        return response

    def get_training_plan(self, user_id: UUID):
        training_plan = self.db.query(TrainingPlanSession).filter(TrainingPlanSession.user_id == user_id).all()
        return [DataClassMapper.to_dict(session) for session in training_plan]
