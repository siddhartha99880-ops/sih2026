from dataclasses import dataclass

from geoalchemy2.shape import to_shape
from sqlalchemy.orm import Session

from app.core.config import get_settings
from app.gis.area import compare_area
from app.gis.geometry import is_valid_geometry
from app.gis.intersection import corridor_intersection
from app.gis.overlap import parcels_overlap
from app.models.parcel import Parcel
from app.schemas.validation import ValidationFindingRead, ValidationResponse


@dataclass(frozen=True)
class ValidationService:
    warning_percent: float = get_settings().area_warning_percent
    conflict_percent: float = get_settings().area_conflict_percent
    corridor_buffer_m: float = get_settings().corridor_buffer_m

    def validate(self, parcel: Parcel, corridor=None, other_parcels: list[Parcel] | None = None) -> ValidationResponse:
        geometry = to_shape(parcel.geometry)
        findings: list[ValidationFindingRead] = []
        valid = is_valid_geometry(geometry)
        findings.append(ValidationFindingRead(code="GEOMETRY_VALID", severity="PASS" if valid else "CONFLICT", message="Parcel geometry is valid." if valid else "Parcel geometry is invalid."))
        if valid:
            comparison = compare_area(parcel.recorded_area_m2, geometry.area, self.warning_percent, self.conflict_percent)
            findings.append(ValidationFindingRead(code="AREA_COMPARISON", severity=comparison.severity, message=f"Recorded area differs from calculated area by {comparison.difference_percent:.1f}%.", calculated_area_m2=comparison.calculated_area_m2))
        if corridor is not None and valid:
            result = corridor_intersection(geometry, corridor, self.corridor_buffer_m)
            if result.intersects:
                findings.append(ValidationFindingRead(code="SPATIAL_CONFLICT", severity="NEEDS_REVIEW", message="Infrastructure corridor intersects the parcel and requires human review.", intersection_area_m2=result.area_m2, intersection_percentage=result.percentage))
        for other in other_parcels or []:
            other_geometry = to_shape(other.geometry)
            if other.id != parcel.id and parcels_overlap(geometry, other_geometry):
                findings.append(ValidationFindingRead(code="PARCEL_OVERLAP", severity="NEEDS_REVIEW", message=f"Parcel overlaps parcel {other.id}; review the source geometries."))
        severity_order = {"PASS": 0, "WARNING": 1, "NEEDS_REVIEW": 2, "CONFLICT": 3}
        overall = max(findings, key=lambda item: severity_order[item.severity]).severity
        return ValidationResponse(parcel_id=parcel.id, findings=findings, overall_severity=overall)