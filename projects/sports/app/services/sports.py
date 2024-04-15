from pydantic import UUID4
from sqlalchemy.orm import Session

from ..models.model import Sport
from ..exceptions.exceptions import NotFoundError


class SportService:
    def __init__(self, db: Session):
        self.db = db

    def get_sports(self):
        sports = self.db.query(Sport).all()
        return [
            {
                "sport_id": str(sport.sport_id),
                "name": str(sport.name),
            }
            for sport in sports
        ]

    def get_sport_by_id(self, sport_id: UUID4):
        sport = self.db.query(Sport).get(sport_id)
        if sport is None:
            raise NotFoundError("Sport Not Found")
        return {
            "sport_id": str(sport.sport_id),
            "name": str(sport.name),
        }
