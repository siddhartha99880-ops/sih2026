from dataclasses import dataclass

from shapely.geometry.base import BaseGeometry


@dataclass(frozen=True)
class IntersectionResult:
    intersects: bool
    area_m2: float
    percentage: float


def corridor_intersection(parcel: BaseGeometry, corridor: BaseGeometry, buffer_m: float = 0.5) -> IntersectionResult:
    impacted = parcel.intersection(corridor.buffer(buffer_m))
    area = float(impacted.area)
    percentage = min(100.0, area / parcel.area * 100) if parcel.area else 0.0
    return IntersectionResult(area > 0, area, percentage)