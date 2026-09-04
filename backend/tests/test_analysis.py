from fastapi.testclient import TestClient

from app.main import app


def test_analysis_returns_conflicts_risk_and_audit_hash() -> None:
    request = {
        "parcel_id": "PARCEL-001",
        "fields": {
            "khasra_number": "214",
            "owner_name": "Synthetic Owner",
            "recorded_area_m2": 1200,
            "ownership_count": 2,
            "dispute_indicator": False,
        },
        "parcel": {
            "type": "Polygon",
            "coordinates": [[[0, 0], [30, 0], [30, 30], [0, 30], [0, 0]]],
        },
        "corridor": {
            "type": "LineString",
            "coordinates": [[-5, 15], [35, 15]],
        },
    }

    response = TestClient(app).post("/api/v1/analyses", json=request)

    assert response.status_code == 200
    body = response.json()
    assert body["lifecycle_status"] == "CONFLICT"
    assert body["risk"]["level"] == "HIGH"
    assert body["corridor_intersection_percent"] > 0
    assert len(body["audit"]["record_hash"]) == 64
    assert {finding["code"] for finding in body["findings"]} >= {"AREA_COMPARISON", "SPATIAL_CONFLICT"}