from uuid import uuid4

import pytest
from fastapi.testclient import TestClient

from app.api.routes.documents import service
from app.db.database import SessionLocal, database_ready
from app.main import app
from app.models.document import DocumentStatus
from app.storage.local import LocalDocumentStorage


pytestmark = pytest.mark.skipif(not database_ready(), reason="PostgreSQL/PostGIS is unavailable")


@pytest.fixture
def processing_context(tmp_path):
    client = TestClient(app)
    previous_storage = service.storage
    service.storage = LocalDocumentStorage(tmp_path, max_size_bytes=1024 * 1024)
    document_ids: list[str] = []

    def upload() -> dict:
        response = client.post(
            "/api/v1/documents",
            files={"file": ("synthetic-processing.pdf", b"%PDF-1.7 processing test", "application/pdf")},
        )
        assert response.status_code == 201
        document = response.json()
        document_ids.append(document["id"])
        return document

    yield client, upload

    for document_id in document_ids:
        client.delete(f"/api/v1/documents/{document_id}")
    service.storage = previous_storage


def transition(client: TestClient, document_id: str, status: DocumentStatus):
    return client.patch(f"/api/v1/documents/{document_id}/status", json={"status": status.value})


def set_status(document_id: str, status: DocumentStatus) -> None:
    with SessionLocal() as session:
        document = service.repository.get(session, document_id)
        assert document is not None
        service.repository.update_status(session, document, status)


def test_upload_starts_ready_for_ocr(processing_context) -> None:
    _, upload = processing_context

    document = upload()

    assert document["status"] == DocumentStatus.READY_FOR_OCR.value


def test_ready_for_ocr_to_ocr_complete_returns_200(processing_context) -> None:
    client, upload = processing_context
    document = upload()

    response = transition(client, document["id"], DocumentStatus.OCR_COMPLETE)

    assert response.status_code == 200
    assert response.json()["status"] == DocumentStatus.OCR_COMPLETE.value


def test_ocr_complete_to_needs_review_returns_200(processing_context) -> None:
    client, upload = processing_context
    document = upload()
    assert transition(client, document["id"], DocumentStatus.OCR_COMPLETE).status_code == 200

    response = transition(client, document["id"], DocumentStatus.NEEDS_REVIEW)

    assert response.status_code == 200
    assert response.json()["status"] == DocumentStatus.NEEDS_REVIEW.value


def test_processing_to_failed_returns_200(processing_context) -> None:
    client, upload = processing_context
    document = upload()
    set_status(document["id"], DocumentStatus.PROCESSING)

    response = transition(client, document["id"], DocumentStatus.FAILED)

    assert response.status_code == 200
    assert response.json()["status"] == DocumentStatus.FAILED.value


def test_ocr_complete_to_failed_returns_200(processing_context) -> None:
    client, upload = processing_context
    document = upload()
    assert transition(client, document["id"], DocumentStatus.OCR_COMPLETE).status_code == 200

    response = transition(client, document["id"], DocumentStatus.FAILED)

    assert response.status_code == 200
    assert response.json()["status"] == DocumentStatus.FAILED.value


def test_invalid_transition_returns_400(processing_context) -> None:
    client, upload = processing_context
    document = upload()

    response = transition(client, document["id"], DocumentStatus.PROCESSING)

    assert response.status_code == 400
    assert response.json()["detail"] == "invalid document status transition"


def test_same_status_transition_returns_400(processing_context) -> None:
    client, upload = processing_context
    document = upload()

    response = transition(client, document["id"], DocumentStatus.READY_FOR_OCR)

    assert response.status_code == 400
    assert response.json()["detail"] == "invalid document status transition"


def test_nonexistent_document_returns_404(processing_context) -> None:
    client, _ = processing_context

    response = transition(client, f"missing-{uuid4().hex}", DocumentStatus.OCR_COMPLETE)

    assert response.status_code == 404
    assert response.json()["detail"] == "document not found"
