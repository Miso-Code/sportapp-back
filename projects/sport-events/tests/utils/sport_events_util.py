from uuid import UUID

from app.models.model import SportEvent
from app.models.schemas.schema import SportEventCreate


def generate_random_sport_event_data(faker):
    return SportEventCreate(
        sport_id=faker.uuid4(),
        location_latitude=faker.latitude(),
        location_longitude=faker.longitude(),
        start_date=faker.date_time_this_year(),
        end_date=faker.date_time_this_year(),
        title=faker.word(),
        capacity=faker.random_int(min=1, max=100),
        description=faker.text(),
    )


def generate_random_sport_event(faker):
    return SportEvent(
        event_id=UUID(faker.uuid4()),
        sport_id=UUID(faker.uuid4()),
        location_latitude=float(faker.latitude()),
        location_longitude=float(faker.longitude()),
        start_date=faker.date_time_this_year(),
        end_date=faker.date_time_this_year(),
        title=faker.word(),
        capacity=faker.random_int(min=1, max=100),
        description=faker.text(),
    )
