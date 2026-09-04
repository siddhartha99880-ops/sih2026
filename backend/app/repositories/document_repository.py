from sqlalchemy import select
from sqlalchemy.orm import Session

from app.models.document import Document, DocumentStatus


class DocumentRepository:
    def create(self, session: Session, document: Document) -> Document:
        session.add(document)
        session.commit()
        session.refresh(document)
        return document

    def get(self, session: Session, document_id: str) -> Document | None:
        return session.get(Document, document_id)

    def update_parcel_id(self, session: Session, document: Document, parcel_id: str | None) -> Document:
        document.parcel_id = parcel_id
        session.commit()
        session.refresh(document)
        return document

    def update_status(self, session: Session, document: Document, status: DocumentStatus) -> Document:
        document.status = status
        session.commit()
        session.refresh(document)
        return document

    def list(self, session: Session, parcel_id: str | None = None, status: DocumentStatus | None = None) -> list[Document]:
        query = select(Document).order_by(Document.created_at)
        if parcel_id is not None:
            query = query.where(Document.parcel_id == parcel_id)
        if status is not None:
            query = query.where(Document.status == status)
        return list(session.scalars(query))

    def delete(self, session: Session, document: Document) -> None:
        session.delete(document)
        session.commit()