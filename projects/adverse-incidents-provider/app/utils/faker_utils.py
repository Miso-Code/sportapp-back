from typing import Any

from faker.providers import BaseProvider


class AdverseIncidentFakerProvider(BaseProvider):
    """A Faker provider for adverse incidents."""

    INCIDENTS = [
        {
            "name": "Shooting",
            "description": "Shooting incident reported in the area.",
        },
        {
            "name": "Robbery",
            "description": "Robbery incident reported in the area.",
        },
        {
            "name": "Fire",
            "description": "Fire incident reported in the area.",
        },
        {
            "name": "Flood",
            "description": "Flood incident reported in the area.",
        },
        {
            "name": "Earthquake",
            "description": "Earthquake incident reported in the area.",
        },
        {
            "name": "Tornado",
            "description": "Tornado incident reported in the area.",
        },
        {
            "name": "Hurricane",
            "description": "Hurricane incident reported in the area.",
        },
        {
            "name": "Tsunami",
            "description": "Tsunami incident reported in the area.",
        },
        {
            "name": "Volcano",
            "description": "Volcano incident reported in the area.",
        },
        {
            "name": "Explosion",
            "description": "Explosion incident reported in the area.",
        },
        {
            "name": "Building Collapse",
            "description": "Building collapse incident reported in the area.",
        },
        {
            "name": "Landslide",
            "description": "Landslide incident reported in the area.",
        },
        {
            "name": "Terrorist Attack",
            "description": "Terrorist attack reported in the area.",
        },
        {
            "name": "Mudslide",
            "description": "Mudslide incident reported in the area.",
        },
        {
            "name": "Chemical Spill",
            "description": "Chemical Spill incident reported in the area.",
        },
        {
            "name": "Animal Attack",
            "description": "Animal attack reported in the area.",
        },
    ]

    def adverse_incident(self) -> str:
        incident = self.random_element(self.INCIDENTS)
        name = incident["name"]
        description = incident["description"]
        return f"{name}: {description}"

    def all_adverse_incidents(self) -> list[dict[str:Any]]:
        return self.INCIDENTS
