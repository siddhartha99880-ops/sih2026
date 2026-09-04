from fastapi import APIRouter, Depends, File, Form, HTTPException, Query, UploadFile, status
from fastapi.responses import FileResponse
from sqlalchemy.orm import Session

from app.db.database import get_db
from app.models.document import DocumentStatus, DocumentType
from app.schemas.document import DocumentParcelAssociationRequest, DocumentResponse
from app.services.document_service import DocumentService


router = APIRouter(prefix="/documents", tags=["documents"])
service = DocumentService()


@router.post("", response_model=DocumentResponse, status_code=status.HTTP_201_CREATED)
def upload_document(
    file: UploadFile = File(...),
    parcel_id: str | None = Form(default=None),
    document_type: DocumentType = Form(default=DocumentType.UNKNOWN),
    session: Session = Depends(get_db),
):
    try:
        return service.to_response(service.upload(session, file, parcel_id, document_type))
    except LookupError as exc:
        raise HTTPException(status_code=404, detail=str(exc)) from exc
    except OverflowError as exc:
        raise HTTPException(status_code=413, detail=str(exc)) from exc
    except ValueError as exc:
        message = str(exc)
        code = 415 if "unsupported" in message or "declared type" in message else 400
        raise HTTPException(status_code=code, detail=message) from exc


@router.get("", response_model=list[DocumentResponse])
def list_documents(parcel_id: str | None = None, status: DocumentStatus | None = None, session: Session = Depends(get_db)):
    return [service.to_response(document) for document in service.repository.list(session, parcel_id, status)]


@router.get("/{document_id}")
def get_document(document_id: str, session: Session = Depends(get_db)):
    document = service.repository.get(session, document_id)
    if document is None:
        raise HTTPException(status_code=404, detail="document not found")
    return service.to_response(document)


@router.patch("/{document_id}/parcel", response_model=DocumentResponse)
def associate_document_parcel(
    document_id: str,
    request: DocumentParcelAssociationRequest,
    session: Session = Depends(get_db),
):
    try:
        document = service.associate_parcel(session, document_id, request.parcel_id)
    except LookupError as exc:
        raise HTTPException(status_code=404, detail=str(exc)) from exc
    return service.to_response(document)


@router.get("/{document_id}/download")
def download_document(document_id: str, session: Session = Depends(get_db)):
    document = service.repository.get(session, document_id)
    if document is None:
        raise HTTPException(status_code=404, detail="document not found")
    try:
        path = service.storage.path_for(document.storage_path)
    except ValueError as exc:
        raise HTTPException(status_code=500, detail="document storage is invalid") from exc
    if not path.is_file():
        raise HTTPException(status_code=404, detail="document file not found")
    return FileResponse(path, media_type=document.mime_type, filename=document.original_filename)


@router.delete("/{document_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_document(document_id: str, session: Session = Depends(get_db)) -> None:
    document = service.repository.get(session, document_id)
    if document is None:
        raise HTTPException(status_code=404, detail="document not found")
    service.delete(session, document)