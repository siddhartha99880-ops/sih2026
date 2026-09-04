from shapely.geometry.base import BaseGeometry


def overlap_area(first: BaseGeometry, second: BaseGeometry) -> float:
    return float(first.intersection(second).area)


def parcels_overlap(first: BaseGeometry, second: BaseGeometry) -> bool:
    return overlap_area(first, second) > 0