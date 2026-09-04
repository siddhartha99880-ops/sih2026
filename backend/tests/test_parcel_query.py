from uuid import uuid4

import pytest
from fastapi.testclient import TestClient

from app.db.database import database_ready
from app.main import app


pytestmark = pytest.mark.skipif(not database_ready(), reason="PostgreSQL/PostGIS is unavailable")


@pytest.fixture
def parcel_client():
    client = TestClient(app)
    prefix = f"QUERY-{uuid4().hex[:8]}"
    parcels = [
        {
            "id": f"{prefix}-A",
            "khasra_number": "K-214",
            "khata_number": "KH-ALPHA",
            "state": "Synthetic State",
            "district": "North District",
            "tehsil": "Central Tehsil",
            "village": "River Village",
        },
        {
            "id": f"{prefix}-B",
            "khasra_number": "K-215",
            "khata_number": "KH-BETA",
            "state": "Synthetic State",
            "district": "North District",
            "tehsil": "West Tehsil",
            "village": "Hill Village",
        },
        {
            "id": f"{prefix}-C",
            "khasra_number": "K-216",
            "khata_number": "KH-GAMMA",
            "state": "Synthetic State",
            "district": "South District",
            "tehsil": "Central Tehsil",
            "village": "River Village",
        },
    ]
    for parcel in parcels:
        response = client.post(
            "/api/v1/parcels",
            json={
                **parcel,
                "recorded_area_m2": 900,
                "srid": 3857,
                "geometry": {"type": "Polygon", "coordinates": [[[0, 0], [30, 0], [30, 30], [0, 30], [0, 0]]]},
            },
        )
        assert response.status_code == 201
    yield client, prefix, parcels
    for parcel in parcels:
        client.delete(f"/api/v1/parcels/{parcel['id']}")


def test_default_list_response_and_total(parcel_client) -> None:
    client, prefix, _ = parcel_client

    response = client.get("/api/v1/parcels")

    assert response.status_code == 200
    body = response.json()
    assert body["total"] >= 3
    assert body["offset"] == 0
    assert body["limit"] == 50
    assert {f"{prefix}-A", f"{prefix}-B", f"{prefix}-C"} <= {item["id"] for item in body["items"]}


def test_search_matches_khasra_khata_and_id_case_insensitively(parcel_client) -> None:
    client, prefix, _ = parcel_client

    assert client.get("/api/v1/parcels", params={"search": "k-214"}).json()["items"][0]["id"] == f"{prefix}-A"
    assert client.get("/api/v1/parcels", params={"search": "kh-beta"}).json()["items"][0]["id"] == f"{prefix}-B"
    assert client.get("/api/v1/parcels", params={"search": prefix.lower()}).json()["total"] == 3


def test_administrative_and_combined_filters_use_and_logic(parcel_client) -> None:
    client, prefix, _ = parcel_client

    filtered = client.get("/api/v1/parcels", params={"search": prefix, "district": "North District"})
    combined = client.get("/api/v1/parcels", params={"search": prefix, "district": "North District", "tehsil": "West Tehsil", "village": "Hill Village", "state": "Synthetic State", "status": "UPLOADED"})

    assert filtered.json()["total"] == 2
    assert combined.json()["total"] == 1
    assert combined.json()["items"][0]["khasra_number"] == "K-215"


def test_pagination_preserves_total_and_requested_window(parcel_client) -> None:
    client, prefix, _ = parcel_client

    response = client.get("/api/v1/parcels", params={"search": prefix, "offset": 1, "limit": 1})

    assert response.status_code == 200
    body = response.json()
    assert body["total"] == 3
    assert body["offset"] == 1
    assert body["limit"] == 1
    assert len(body["items"]) == 1
    assert body["items"][0]["id"] == f"{prefix}-B"


def test_invalid_pagination_is_rejected(parcel_client) -> None:
    client, prefix, _ = parcel_client

    assert client.get("/api/v1/parcels", params={"search": prefix, "limit": 0}).status_code == 422
    assert client.get("/api/v1/parcels", params={"search": prefix, "limit": 101}).status_code == 422
    assert client.get("/api/v1/parcels", params={"search": prefix, "offset": -1}).status_code == 422


def test_existing_single_get_and_mutations_still_work(parcel_client) -> None:
    client, prefix, parcels = parcel_client
    parcel_id = parcels[0]["id"]

    assert client.get(f"/api/v1/parcels/{parcel_id}").status_code == 200
    replacement = {
        **parcels[0],
        "recorded_area_m2": 810,
        "srid": 3857,
        "geometry": {"type": "Polygon", "coordinates": [[[0, 0], [30, 0], [30, 30], [0, 30], [0, 0]]]},
    }
    assert client.put(f"/api/v1/parcels/{parcel_id}", json=replacement).status_code == 200
    assert client.delete(f"/api/v1/parcels/{parcel_id}").status_code == 204
    assert client.get(f"/api/v1/parcels/{parcel_id}").status_code == 404
    client.post(
        "/api/v1/parcels",
        json={
            **replacement,
            "recorded_area_m2": 900,
        },
    )
