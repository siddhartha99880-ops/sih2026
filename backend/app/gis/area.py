from dataclasses import dataclass

from shapely.geometry.base import BaseGeometry


@dataclass(frozen=True)
class AreaComparison:
    calculated_area_m2: float
    difference_percent: float
    severity: str


def calculate_area_m2(geometry: BaseGeometry) -> float:
    return float(geometry.area)


def compare_area(recorded_area_m2: float, calculated_area_m2: float, warning_percent: float, conflict_percent: float) -> AreaComparison:
    if recorded_area_m2 <= 0:
        raise ValueError("recorded area must be positive")
    difference = abs(recorded_area_m2 - calculated_area_m2) / recorded_area_m2 * 100
    severity = "CONFLICT" if difference > conflict_percent else "WARNING" if difference > warning_percent else "PASS"
    return AreaComparison(calculated_area_m2, difference, severity)