import hashlib
from uuid import uuid4

import pytest
from fastapi.testclient import TestClient

from app.api.routes.documents import service
from app.db.database import database_ready
from app.main import app
from app.storage.local import LocalDocumentStorage


pytestmark = pytest.mark.skipif(not database_ready(), reason="PostgreSQL/PostGIS is unavailable")


@pytest.fixture
def client(tmp_path):
    previous_storage = service.storage
    service.storage = LocalDocumentStorage(tmp_path, max_size_bytes=1024 * 1024)
    yield TestClient(app)
    service.storage = previous_storage


def parcel_payload(parcel_id: str) -> dict:
    return {
        "id": parcel_id,
        "khasra_number": "214",
        "state": "Synthetic State",
        "district": "Synthetic District",
        "village": "Synthetic Village",
        "recorded_area_m2": 900,
        "srid": 3857,
        "geometry": {"type": "Polygon", "coordinates": [[[0, 0], [30, 0], [30, 30], [0, 30], [0, 0]]] },
    }


def test_upload_metadata_download_and_delete(client) -> None:
    parcel_id = f"DOC-TEST-{uuid4().hex}"
    document_id = None
    parcel_response = client.post("/api/v1/parcels", json=parcel_payload(parcel_id))
    assert parcel_response.status_code == 201
    content = b"%PDF-1.7 synthetic deed"
    try:
        upload_response = client.post(
            "/api/v1/documents",
            files={"file": ("../../synthetic-deed.pdf", content, "application/pdf")},
            data={"parcel_id": parcel_id, "document_type": "LAND_DEED"},
        )
        assert upload_response.status_code == 201
        metadata = upload_response.json()
        document_id = metadata["id"]
        assert metadata["parcel_id"] == parcel_id
        assert metadata["original_filename"] == "synthetic-deed.pdf"
        assert metadata["status"] == "READY_FOR_OCR"
        assert metadata["checksum_sha256"] == hashlib.sha256(content).hexdigest()
        assert "storage_path" not in metadata

        assert client.get(f"/api/v1/documents/{document_id}").status_code == 200
        assert client.get(f"/api/v1/documents?parcel_id={parcel_id}").json()[0]["id"] == document_id
        download = client.get(f"/api/v1/documents/{document_id}/download")
        assert download.status_code == 200
        assert download.content == content

        delete_response = client.delete(f"/api/v1/documents/{document_id}")
        assert delete_response.status_code == 204
        assert client.get(f"/api/v1/documents/{document_id}").status_code == 404
        document_id = None
    finally:
        if document_id is not None:
            client.delete(f"/api/v1/documents/{document_id}")
        client.delete(f"/api/v1/parcels/{parcel_id}")


def test_upload_rejects_missing_parcel(client) -> None:
    response = client.post(
        "/api/v1/documents",
        files={"file": ("synthetic.pdf", b"%PDF-1.7", "application/pdf")},
        data={"parcel_id": "does-not-exist"},
    )
    assert response.status_code == 404