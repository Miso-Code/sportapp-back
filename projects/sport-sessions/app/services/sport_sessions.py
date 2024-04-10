from pydantic import UUID4
from sqlalchemy.orm import Session

from app.models.model import SportSession, Location
from app.exceptions.exceptions import NotFoundError, NotActiveError
from app.models.schemas.schema import SportSessionFinish, SportSessionStart, SportSessionLocationCreate

from app.services.utils import estimate_distance, estimate_calories_burned, estimate_speed
from app.config.settings import Config


class SportSessionService:
    def __init__(self, db: Session):
        self.db = db

    def get_sport_session(self, sport_session_id: UUID4):
        sport_session = self.db.query(SportSession).filter(SportSession.session_id == sport_session_id).first()

        if not sport_session:
            raise NotFoundError(Config.NOT_FOUND_MESSAGE)

        return {
            "session_id": str(sport_session.session_id),
            "sport_id": str(sport_session.sport_id),
            "user_id": str(sport_session.user_id),
            "started_at": str(sport_session.started_at),
            "duration": int(sport_session.duration) if sport_session.duration else None,
            "steps": int(sport_session.steps) if sport_session.steps else None,
            "distance": float(sport_session.distance) if sport_session.distance else None,
            "calories": float(sport_session.calories) if sport_session.calories else None,
            "average_speed": float(sport_session.average_speed) if sport_session.average_speed else None,
            "min_heartrate": float(sport_session.min_heartrate) if sport_session.min_heartrate else None,
            "max_heartrate": float(sport_session.max_heartrate) if sport_session.max_heartrate else None,
            "avg_heartrate": float(sport_session.avg_heartrate) if sport_session.avg_heartrate else None,
        }

    def start_sport_session(self, sport_session_input: SportSessionStart):
        sport_session = SportSession(sport_id=sport_session_input.sport_id, user_id=sport_session_input.user_id, started_at=sport_session_input.started_at, is_active=True)
        self.db.add(sport_session)
        self.db.commit()
        self.db.refresh(sport_session)

        initial_location = Location(
            session_id=sport_session.session_id,
            latitude=sport_session_input.initial_location.latitude,
            longitude=sport_session_input.initial_location.longitude,
            accuracy=sport_session_input.initial_location.accuracy,
            altitude=sport_session_input.initial_location.altitude,
            altitude_accuracy=sport_session_input.initial_location.altitude_accuracy,
            heading=sport_session_input.initial_location.heading,
            speed=sport_session_input.initial_location.speed,
        )

        self.db.add(initial_location)
        self.db.commit()

        return {
            "session_id": str(sport_session.session_id),
            "sport_id": str(sport_session.sport_id),
            "user_id": str(sport_session.user_id),
            "started_at": sport_session.started_at.isoformat(),
        }

    def add_location_to_sport_session(self, sport_session_id: UUID4, location: SportSessionLocationCreate):
        sport_session: SportSession = self.db.query(SportSession).filter(SportSession.session_id == sport_session_id).first()

        if not sport_session:
            raise NotFoundError(Config.NOT_FOUND_MESSAGE)

        if not sport_session.is_active:
            raise NotActiveError("Sport session is already finished")

        location_payload = {
            "session_id": sport_session_id,
            "latitude": location.latitude,
            "longitude": location.longitude,
            "accuracy": location.accuracy,
            "altitude": location.altitude,
            "altitude_accuracy": location.altitude_accuracy,
            "heading": location.heading,
            "speed": location.speed,
        }

        new_location = Location(**location_payload)

        self.db.add(new_location)
        self.db.commit()

        return {
            "session_id": str(sport_session.session_id),
            "latitude": float(location.latitude),
            "longitude": float(location.longitude),
            "accuracy": float(location.accuracy),
            "altitude": float(location.altitude),
            "altitude_accuracy": float(location.altitude_accuracy),
            "heading": float(location.heading),
            "speed": float(location.speed),
        }

    def finish_sport_session(self, sport_session_id: UUID4, sport_session_input: SportSessionFinish):
        sport_session: SportSession = self.db.query(SportSession).filter(SportSession.session_id == sport_session_id).first()

        if not sport_session:
            raise NotFoundError(Config.NOT_FOUND_MESSAGE)

        elif not sport_session.is_active:
            raise NotActiveError("Sport session is already finished")

        if sport_session_input.distance is None:
            sport_session_input.distance = estimate_distance(sport_session_input.steps, sport_session.locations)

        if sport_session_input.calories is None:
            sport_session_input.calories = estimate_calories_burned(sport_session_input.steps)

        if sport_session_input.average_speed is None:
            sport_session_input.average_speed = estimate_speed(sport_session_input.distance, sport_session_input.duration, sport_session.locations)

        sport_session.duration = sport_session_input.duration
        sport_session.steps = sport_session_input.steps
        sport_session.distance = sport_session_input.distance
        sport_session.calories = sport_session_input.calories
        sport_session.average_speed = sport_session_input.average_speed
        sport_session.min_heartrate = sport_session_input.min_heartrate
        sport_session.max_heartrate = sport_session_input.max_heartrate
        sport_session.avg_heartrate = sport_session_input.avg_heartrate
        sport_session.is_active = False

        self.db.commit()
        self.db.refresh(sport_session)

        return {
            "session_id": str(sport_session.session_id),
            "sport_id": str(sport_session.sport_id),
            "user_id": str(sport_session.user_id),
            "started_at": str(sport_session.started_at),
            "duration": int(sport_session.duration),
            "steps": int(sport_session.steps) if sport_session.steps else None,
            "distance": float(sport_session.distance) if sport_session.distance else None,
            "calories": float(sport_session.calories) if sport_session.calories else None,
            "average_speed": float(sport_session.average_speed) if sport_session.average_speed else None,
            "min_heartrate": float(sport_session.min_heartrate) if sport_session.min_heartrate else None,
            "max_heartrate": float(sport_session.max_heartrate) if sport_session.max_heartrate else None,
            "avg_heartrate": float(sport_session.avg_heartrate) if sport_session.avg_heartrate else None,
        }
