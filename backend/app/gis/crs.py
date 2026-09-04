from functools import lru_cache

from pyproj import Transformer
from shapely.ops import transform
from shapely.geometry.base import BaseGeometry


@lru_cache
def _transformer(source_srid: int, target_srid: int) -> Transformer:
    return Transformer.from_crs(source_srid, target_srid, always_xy=True)


def transform_geometry(geometry: BaseGeometry, source_srid: int, target_srid: int) -> BaseGeometry:
    if source_srid == target_srid:
        return geometry
    return transform(_transformer(source_srid, target_srid).transform, geometry)


def validate_srid(srid: int) -> int:
    if srid <= 0:
        raise ValueError("SRID must be a positive EPSG code")
    return srid