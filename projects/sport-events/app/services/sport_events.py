from uuid import UUID

from sqlalchemy import or_
from sqlalchemy.orm import Session

from app.exceptions.exceptions import NotFoundError
from app.models.mappers.data_mapper import DataClassMapper
from app.models.model import SportEvent
from app.models.schemas.schema import SportEventCreate


class SportEventsService:
    def __init__(self, db: Session):
        self.db = db

    def create_sport_event(self, sport_event_create: SportEventCreate):
        sport_event = SportEvent(**sport_event_create.dict())
        self.db.add(sport_event)
        self.db.commit()

        return DataClassMapper.to_dict(sport_event)

    def get_sport_events(self, search, offset, limit):
        if search:
            events = (
                self.db.query(SportEvent)
                .filter(
                    or_(
                        SportEvent.title.ilike(f"%{search}%"),
                        SportEvent.description.ilike(f"%{search}%"),
                    ),
                )
                .order_by(SportEvent.start_date.desc())
                .offset(offset)
                .limit(limit)
                .all()
            )
        else:
            events = self.db.query(SportEvent).order_by(SportEvent.start_date.desc()).offset(offset).limit(limit).all()

        return [DataClassMapper.to_dict(event) for event in events]

    def get_sport_event(self, sport_event_id: UUID):
        sport_event = self._get_sport_event_by_id(sport_event_id)
        return DataClassMapper.to_dict(sport_event)

    def _get_sport_event_by_id(self, sport_event_id):
        sport_event = self.db.query(SportEvent).filter(SportEvent.event_id == sport_event_id).first()
        if not sport_event:
            raise NotFoundError("Sport event not found")

        return sport_event
