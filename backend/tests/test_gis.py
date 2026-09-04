import pytest
from shapely.geometry import LineString, Polygon

from app.gis.area import compare_area
from app.gis.crs import transform_geometry
from app.gis.geometry import is_valid_geometry
from app.gis.intersection import corridor_intersection
from app.gis.overlap import parcels_overlap


def test_geometry_validity_and_area_thresholds() -> None:
    parcel = Polygon([(0, 0), (10, 0), (10, 10), (0, 10), (0, 0)])
    assert is_valid_geometry(parcel)
    assert compare_area(100, 100, 5, 10).severity == "PASS"
    assert compare_area(105, 100, 5, 10).severity == "PASS"
    assert compare_area(110, 100, 5, 10).severity == "WARNING"
    assert compare_area(120, 100, 5, 10).severity == "CONFLICT"


def test_invalid_geometry_and_overlap_cases() -> None:
    invalid = Polygon([(0, 0), (10, 10), (0, 10), (10, 0), (0, 0)])
    assert not is_valid_geometry(invalid)
    first = Polygon([(0, 0), (10, 0), (10, 10), (0, 10), (0, 0)])
    overlapping = Polygon([(5, 5), (15, 5), (15, 15), (5, 15), (5, 5)])
    separate = Polygon([(20, 20), (30, 20), (30, 30), (20, 30), (20, 20)])
    assert parcels_overlap(first, overlapping)
    assert not parcels_overlap(first, separate)


def test_corridor_intersection_and_crs_transform() -> None:
    parcel = Polygon([(0, 0), (10, 0), (10, 10), (0, 10), (0, 0)])
    result = corridor_intersection(parcel, LineString([(-1, 5), (11, 5)]))
    assert result.intersects
    assert result.area_m2 > 0
    assert not corridor_intersection(parcel, LineString([(20, 20), (30, 20)])).intersects
    transformed = transform_geometry(Polygon([(77, 12), (77.001, 12), (77.001, 12.001), (77, 12.001)]), 4326, 3857)
    assert transformed.area > 0


def test_area_rejects_non_positive_recorded_area() -> None:
    with pytest.raises(ValueError):
        compare_area(0, 10, 5, 10)