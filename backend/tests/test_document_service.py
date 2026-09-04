from io import BytesIO

import pytest
from fastapi import UploadFile
from starlette.datastructures import Headers

from app.schemas.document import DocumentType
from app.services.document_service import DocumentService
from app.storage.local import LocalDocumentStorage


class MissingDatabaseRepository:
    def create(self, session, document):
        raise RuntimeError("synthetic database failure")


class NoParcelRepository:
    def get(self, session, parcel_id):
        return None


def test_database_failure_removes_saved_file(tmp_path) -> None:
    service = DocumentService(
        repository=MissingDatabaseRepository(),
        parcel_repository=NoParcelRepository(),
        storage=LocalDocumentStorage(tmp_path, max_size_bytes=1024),
    )
    upload = UploadFile(
        BytesIO(b"%PDF-1.7 synthetic"),
        filename="deed.pdf",
        headers=Headers({"content-type": "application/pdf"}),
    )
    with pytest.raises(RuntimeError, match="database failure"):
        service.upload(None, upload, None, DocumentType.LAND_DEED)
    assert not list(tmp_path.rglob("*"))