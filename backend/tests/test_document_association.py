from uuid import uuid4

import pytest
from fastapi.testclient import TestClient

from app.api.routes.documents import service
from app.db.database import database_ready
from app.main import app
from app.storage.local import LocalDocumentStorage


pytestmark = pytest.mark.skipif(not database_ready(), reason="PostgreSQL/PostGIS is unavailable")


@pytest.fixture
def association_context(tmp_path):
    client = TestClient(app)
    previous_storage = service.storage
    service.storage = LocalDocumentStorage(tmp_path, max_size_bytes=1024 * 1024)
    suffix = uuid4().hex
    parcel_ids = [f"ASSOC-A-{suffix}", f"ASSOC-B-{suffix}"]
    for parcel_id in parcel_ids:
        response = client.post(
            "/api/v1/parcels",
            json={
                "id": parcel_id,
                "khasra_number": "214",
                "state": "Synthetic State",
                "district": "Synthetic District",
                "village": "Synthetic Village",
                "recorded_area_m2": 900,
                "srid": 3857,
                "geometry": {"type": "Polygon", "coordinates": [[[0, 0], [30, 0], [30, 30], [0, 30], [0, 0]]]},
            },
        )
        assert response.status_code == 201
    document_ids: list[str] = []

    def upload(parcel_id: str | None = None) -> dict:
        response = client.post(
            "/api/v1/documents",
            files={"file": ("synthetic.pdf", b"%PDF-1.7 association test", "application/pdf")},
            data={"parcel_id": parcel_id} if parcel_id is not None else {},
        )
        assert response.status_code == 201
        document = response.json()
        document_ids.append(document["id"])
        return document

    yield client, parcel_ids, upload

    for document_id in document_ids:
        client.delete(f"/api/v1/documents/{document_id}")
    for parcel_id in parcel_ids:
        client.delete(f"/api/v1/parcels/{parcel_id}")
    service.storage = previous_storage


def associate(client: TestClient, document_id: str, parcel_id: str | None):
    return client.patch(f"/api/v1/documents/{document_id}/parcel", json={"parcel_id": parcel_id})


def test_associate_unassociated_document_with_existing_parcel(association_context) -> None:
    client, parcel_ids, upload = association_context
    document = upload()

    response = associate(client, document["id"], parcel_ids[0])

    assert response.status_code == 200
    assert response.json()["parcel_id"] == parcel_ids[0]


def test_change_existing_document_association(association_context) -> None:
    client, parcel_ids, upload = association_context
    document = upload(parcel_ids[0])

    response = associate(client, document["id"], parcel_ids[1])

    assert response.status_code == 200
    assert response.json()["parcel_id"] == parcel_ids[1]


def test_remove_document_association_with_null(association_context) -> None:
    client, parcel_ids, upload = association_context
    document = upload(parcel_ids[0])

    response = associate(client, document["id"], None)

    assert response.status_code == 200
    assert response.json()["parcel_id"] is None


def test_association_rejects_nonexistent_document(association_context) -> None:
    client, _, _ = association_context

    response = associate(client, f"missing-{uuid4().hex}", None)

    assert response.status_code == 404
    assert response.json()["detail"] == "document not found"


def test_association_rejects_nonexistent_parcel(association_context) -> None:
    client, _, upload = association_context
    document = upload()

    response = associate(client, document["id"], f"missing-{uuid4().hex}")

    assert response.status_code == 404
    assert response.json()["detail"] == "parcel not found"


def test_document_listing_by_parcel_still_works(association_context) -> None:
    client, parcel_ids, upload = association_context
    document = upload()
    assert associate(client, document["id"], parcel_ids[0]).status_code == 200

    response = client.get("/api/v1/documents", params={"parcel_id": parcel_ids[0]})

    assert response.status_code == 200
    assert [item["id"] for item in response.json()] == [document["id"]]
