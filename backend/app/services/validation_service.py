from dataclasses import dataclass

from pyproj import CRS
from pyproj.exceptions import CRSError
from geoalchemy2.shape import to_shape
from sqlalchemy.orm import Session

from app.core.config import get_settings
from app.core.errors import AppValidationError
from app.gis.area import calculate_area_m2, compare_area
from app.gis.geometry import is_valid_geometry
from app.gis.intersection import corridor_intersection
from app.gis.crs import transform_geometry, validate_srid
from app.gis.overlap import overlap_area, parcels_overlap
from app.models.parcel import Parcel
from app.schemas.validation import OverlapResultRead, ValidationFindingRead, ValidationResponse


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
        try:
            validate_srid(parcel.srid)
            parcel_crs = CRS.from_epsg(parcel.srid)
        except (CRSError, ValueError, RuntimeError) as exc:
            raise AppValidationError(message="parcel CRS is invalid") from exc
        calculated_area = None
        area_difference = None
        area_difference_percent = None
        if parcel_crs.is_geographic:
            findings.append(ValidationFindingRead(code="CRS_AREA_POLICY", severity="NEEDS_REVIEW", message="Geographic coordinates cannot be used directly for authoritative square-metre area calculation."))
        elif valid:
            calculated_area = calculate_area_m2(geometry)
            comparison = compare_area(parcel.recorded_area_m2, calculated_area, self.warning_percent, self.conflict_percent)
            area_difference = abs(parcel.recorded_area_m2 - calculated_area)
            area_difference_percent = comparison.difference_percent
            findings.append(ValidationFindingRead(code="AREA_COMPARISON", severity=comparison.severity, message=f"Recorded area differs from calculated area by {comparison.difference_percent:.1f}%.", calculated_area_m2=comparison.calculated_area_m2))
        if corridor is not None and valid:
            result = corridor_intersection(geometry, corridor, self.corridor_buffer_m)
            if result.intersects:
                findings.append(ValidationFindingRead(code="SPATIAL_CONFLICT", severity="NEEDS_REVIEW", message="Infrastructure corridor intersects the parcel and requires human review.", intersection_area_m2=result.area_m2, intersection_percentage=result.percentage))
        overlap_results: list[OverlapResultRead] = []
        if valid:
            for other in other_parcels or []:
                other_geometry = to_shape(other.geometry)
                if other.srid != parcel.srid:
                    try:
                        other_geometry = transform_geometry(other_geometry, other.srid, parcel.srid)
                    except (CRSError, ValueError, RuntimeError) as exc:
                        raise AppValidationError(message="parcel CRS is invalid") from exc
                if other.id != parcel.id and parcels_overlap(geometry, other_geometry):
                    area = overlap_area(geometry, other_geometry)
                    percentage = area / geometry.area * 100 if geometry.area else 0
                    overlap_results.append(OverlapResultRead(parcel_id=other.id, overlap_area_m2=area, overlap_percentage=percentage))
                    findings.append(ValidationFindingRead(code="PARCEL_OVERLAP", severity="NEEDS_REVIEW", message=f"Parcel has positive-area overlap with parcel {other.id}; review the source geometries."))
        severity_order = {"PASS": 0, "WARNING": 1, "NEEDS_REVIEW": 2, "CONFLICT": 3}
        overall = max(findings, key=lambda item: severity_order[item.severity]).severity
        overlap_detected = bool(overlap_results)
        if overlap_detected and severity_order[overall] < severity_order["NEEDS_REVIEW"]:
            overall = "NEEDS_REVIEW"
        summaries = {
            "PASS": "Parcel geometry, area, and overlap checks passed.",
            "WARNING": "Parcel validation found an area warning that requires review.",
            "CONFLICT": "Parcel validation found a geometry conflict.",
            "NEEDS_REVIEW": "Parcel validation found an issue requiring human review.",
        }
        return ValidationResponse(
            parcel_id=parcel.id,
            geometry_valid=valid,
            calculated_area_m2=calculated_area,
            recorded_area_m2=parcel.recorded_area_m2,
            area_difference_m2=area_difference,
            area_difference_percent=area_difference_percent,
            overlap_detected=overlap_detected,
            overlapping_parcel_ids=[item.parcel_id for item in overlap_results],
            overlap_results=overlap_results,
            result=overall,
            summary=summaries[overall],
            findings=findings,
            overall_severity=overall,
        )