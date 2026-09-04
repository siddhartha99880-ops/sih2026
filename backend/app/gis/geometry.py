from typing import Any

from shapely.geometry import shape
from shapely.geometry.base import BaseGeometry


def geometry_from_geojson(geojson: dict[str, Any]) -> BaseGeometry:
    geometry = shape(geojson)
    if geometry.is_empty:
        raise ValueError("geometry must not be empty")
    return geometry


def geometry_to_geojson(geometry: BaseGeometry) -> dict[str, Any]:
    return geometry.__geo_interface__


def is_valid_geometry(geometry: BaseGeometry) -> bool:
    return geometry.is_valid and not geometry.is_empty