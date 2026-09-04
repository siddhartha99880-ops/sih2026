from types import SimpleNamespace
from uuid import uuid4

import pytest
from fastapi.testclient import TestClient
from geoalchemy2.shape import from_shape
from shapely.geometry import Polygon

from app.db.database import database_ready
from app.core.errors import AppValidationError
from app.gis.crs import transform_geometry
from app.main import app
from app.services.validation_service import ValidationService


def parcel(parcel_id: str, geometry: Polygon, recorded_area_m2: float, srid: int = 3857):
    return SimpleNamespace(
        id=parcel_id,
        geometry=from_shape(geometry, srid=srid),
        recorded_area_m2=recorded_area_m2,
        srid=srid,
    )


def square(points: list[tuple[float, float]]) -> Polygon:
    return Polygon(points)


def test_matching_area_is_pass_and_returns_metrics() -> None:
    geometry = square([(0, 0), (10, 0), (10, 10), (0, 10), (0, 0)])

    result = ValidationService().validate(parcel("VALID-1", geometry, 100), other_parcels=[])

    assert result.result == "PASS"
    assert result.geometry_valid is True
    assert result.calculated_area_m2 == 100
    assert result.area_difference_m2 == 0
    assert result.area_difference_percent == 0
    assert result.overlap_detected is False


def test_area_difference_at_or_below_five_percent_is_not_conflict() -> None:
    geometry = square([(0, 0), (10, 0), (10, 10), (0, 10), (0, 0)])

    result = ValidationService().validate(parcel("VALID-2", geometry, 104), other_parcels=[])

    assert result.area_difference_percent < 5
    assert result.result == "PASS"


def test_area_difference_above_five_percent_is_warning() -> None:
    geometry = square([(0, 0), (10, 0), (10, 10), (0, 10), (0, 0)])

    result = ValidationService().validate(parcel("AREA-WARN", geometry, 110), other_parcels=[])

    assert result.area_difference_percent > 5
    assert result.result == "WARNING"
    assert result.findings[1].severity == "WARNING"


def test_invalid_geometry_is_not_pass() -> None:
    geometry = square([(0, 0), (10, 10), (0, 10), (10, 0), (0, 0)])

    result = ValidationService().validate(parcel("INVALID-1", geometry, 100), other_parcels=[])

    assert result.geometry_valid is False
    assert result.result == "CONFLICT"


def test_invalid_geometry_does_not_report_overlap() -> None:
    invalid_geometry = square([(0, 0), (10, 10), (0, 10), (10, 0), (0, 0)])
    other_geometry = square([(1, 1), (9, 1), (9, 9), (1, 9), (1, 1)])

    result = ValidationService().validate(
        parcel("INVALID-OVERLAP", invalid_geometry, 100),
        other_parcels=[parcel("OTHER-PARCEL", other_geometry, 64)],
    )

    assert result.result == "CONFLICT"
    assert result.overlap_detected is False
    assert result.overlapping_parcel_ids == []


def test_different_projected_srids_are_transformed_for_overlap() -> None:
    source_geometry = square([(77, 12), (77.001, 12), (77.001, 12.001), (77, 12.001), (77, 12)])
    target_geometry = transform_geometry(source_geometry, 4326, 3857)
    other_geometry = transform_geometry(target_geometry, 3857, 32643)
    target = parcel("SRID-TARGET", target_geometry, target_geometry.area)

    result = ValidationService().validate(
        target,
        other_parcels=[parcel("SRID-OTHER", other_geometry, other_geometry.area, srid=32643)],
    )

    assert result.overlap_detected is True
    assert result.overlapping_parcel_ids == ["SRID-OTHER"]
    assert result.overlap_results[0].overlap_area_m2 > 0


def test_invalid_srid_raises_safe_app_validation_error() -> None:
    geometry = square([(0, 0), (10, 0), (10, 10), (0, 10), (0, 0)])

    with pytest.raises(AppValidationError, match="parcel CRS is invalid"):
        ValidationService().validate(parcel("BAD-SRID", geometry, 100, srid=999999), other_parcels=[])


def test_positive_area_overlap_is_reported_but_boundary_touch_is_not() -> None:
    target_geometry = square([(0, 0), (10, 0), (10, 10), (0, 10), (0, 0)])
    overlapping_geometry = square([(5, 5), (15, 5), (15, 15), (5, 15), (5, 5)])
    touching_geometry = square([(10, 0), (20, 0), (20, 10), (10, 10), (10, 0)])
    target = parcel("OVERLAP-TARGET", target_geometry, 100)

    result = ValidationService().validate(
        target,
        other_parcels=[
            parcel("OVERLAP-OTHER", overlapping_geometry, 100),
            parcel("TOUCHING-OTHER", touching_geometry, 100),
        ],
    )

    assert result.overlap_detected is True
    assert result.overlapping_parcel_ids == ["OVERLAP-OTHER"]
    assert result.overlap_results[0].overlap_area_m2 == 25
    assert result.result == "NEEDS_REVIEW"


def test_parcel_is_not_reported_as_overlapping_itself() -> None:
    geometry = square([(0, 0), (10, 0), (10, 10), (0, 10), (0, 0)])
    target = parcel("SELF-ONLY", geometry, 100)

    result = ValidationService().validate(target, other_parcels=[target])

    assert result.overlap_detected is False
    assert result.overlapping_parcel_ids == []


@pytest.mark.skipif(not database_ready(), reason="PostgreSQL/PostGIS is unavailable")
def test_missing_parcel_uses_centralized_error_contract() -> None:
    response = TestClient(app).post(f"/api/v1/validation/parcel/MISSING-{uuid4().hex}")

    assert response.status_code == 404
    assert response.json() == {"error": {"code": "RESOURCE_NOT_FOUND", "message": "parcel not found"}}