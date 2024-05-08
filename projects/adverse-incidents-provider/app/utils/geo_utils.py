from typing import List

from shapely import Point
from shapely.geometry import Polygon
import numpy as np

from app.config.settings import Config
from app.models.schemas.schema import Coordinate


def generate_random_points(num_points, boundary_coords: List[Coordinate]):
    if boundary_coords is None or len(boundary_coords) == 0:
        boundary_coords = Config.CALI_BOUNDARY_CODES

    boundaries_formatted = [[cords.latitude, cords.longitude] for cords in boundary_coords]
    boundary_polygon = Polygon(boundaries_formatted)
    points = []
    while len(points) < num_points:
        min_x, min_y, max_x, max_y = boundary_polygon.bounds
        random_point = Point(np.random.uniform(min_x, max_x), np.random.uniform(min_y, max_y))
        if random_point.within(boundary_polygon):
            points.append(random_point)

    return points
