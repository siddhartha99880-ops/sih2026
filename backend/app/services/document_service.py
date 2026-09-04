from pathlib import Path
from uuid import uuid4

from fastapi import UploadFile
from sqlalchemy.orm import Session

from app.core.config import get_settings
from app.models.document import Document, DocumentStatus, DocumentType
from app.repositories.document_repository import DocumentRepository
from app.repositories.parcel_repository import ParcelRepository
from app.schemas.document import DocumentResponse
from app.storage.local import LocalDocumentStorage


class DocumentService:
    allowed_status_transitions: dict[DocumentStatus, set[DocumentStatus]] = {
        DocumentStatus.UPLOADED: {DocumentStatus.VALIDATED, DocumentStatus.FAILED},
        DocumentStatus.VALIDATED: {DocumentStatus.PROCESSING, DocumentStatus.FAILED},
        DocumentStatus.PROCESSING: {DocumentStatus.READY_FOR_OCR, DocumentStatus.FAILED},
        DocumentStatus.READY_FOR_OCR: {DocumentStatus.OCR_COMPLETE},
        DocumentStatus.OCR_COMPLETE: {DocumentStatus.NEEDS_REVIEW, DocumentStatus.FAILED},
    }

    def __init__(self, repository: DocumentRepository | None = None, parcel_repository: ParcelRepository | None = None, storage: LocalDocumentStorage | None = None) -> None:
        settings = get_settings()
        self.repository = repository or DocumentRepository()
        self.parcel_repository = parcel_repository or ParcelRepository()
        self.storage = storage or LocalDocumentStorage(settings.document_storage_path, settings.max_document_size_mb * 1024 * 1024)

    def upload(self, session: Session, upload: UploadFile, parcel_id: str | None, document_type: DocumentType) -> Document:
        if parcel_id is not None and self.parcel_repository.get(session, parcel_id) is None:
            raise LookupError("parcel not found")
        document_id = uuid4().hex
        stored = None
        try:
            stored = self.storage.save(upload, document_id)
            document = Document(
                id=document_id,
                parcel_id=parcel_id,
                original_filename=Path(upload.filename or "document").name,
                stored_filename=stored.stored_filename,
                storage_path=stored.storage_path,
                mime_type=upload.content_type or "application/octet-stream",
                file_size_bytes=stored.file_size_bytes,
                document_type=document_type,
                status=DocumentStatus.READY_FOR_OCR,
                checksum_sha256=stored.checksum_sha256,
            )
            return self.repository.create(session, document)
        except Exception:
            if stored is not None:
                self.storage.delete(stored.storage_path)
            raise

    @staticmethod
    def to_response(document: Document) -> DocumentResponse:
        return DocumentResponse.model_validate(document, from_attributes=True)

    def associate_parcel(self, session: Session, document_id: str, parcel_id: str | None) -> Document:
        document = self.repository.get(session, document_id)
        if document is None:
            raise LookupError("document not found")
        if parcel_id is not None and self.parcel_repository.get(session, parcel_id) is None:
            raise LookupError("parcel not found")
        return self.repository.update_parcel_id(session, document, parcel_id)

    def transition_status(self, session: Session, document_id: str, target_status: DocumentStatus) -> Document:
        document = self.repository.get(session, document_id)
        if document is None:
            raise LookupError("document not found")
        if target_status not in self.allowed_status_transitions.get(document.status, set()):
            raise ValueError("invalid document status transition")
        return self.repository.update_status(session, document, target_status)

    def delete(self, session: Session, document: Document) -> None:
        self.repository.delete(session, document)
        self.storage.delete(document.storage_path)