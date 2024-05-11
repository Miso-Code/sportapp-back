import random
from typing import List

import faker

from app.config.settings import Config
from app.models.schemas.schema import AdverseIncident, BoundingBox, Coordinate
from app.utils import geo_utils, faker_utils

fake = faker.Faker()
fake.add_provider(faker_utils.AdverseIncidentFakerProvider)


class AdverseIncidentsProviderService:

    @staticmethod
    def randomize_adverse_incidents(boundaries: List[Coordinate]):
        number_of_incidents = random.randint(1, Config.MAX_ADVERSE_INCIDENTS)
        points = geo_utils.generate_random_points(number_of_incidents, boundaries)
        incidents = []
        for i in range(number_of_incidents):
            point = points[i]
            point_latitude = point.y
            point_longitude = point.x
            affected_range = float(Config.ADVERSE_INCIDENTS_AFFECTED_RANGE)
            incidents.append(
                AdverseIncident(
                    description=fake.adverse_incident(),
                    bounding_box=BoundingBox(
                        latitude_from=point_latitude - affected_range,
                        longitude_from=point_longitude - affected_range,
                        latitude_to=point_latitude + affected_range,
                        longitude_to=point_longitude + affected_range,
                    ),
                ),
            )

        return [incident.dict() for incident in incidents]
