from datetime import datetime
from typing import Annotated

from pydantic import BaseModel, Field

from app.models.document import DocumentStatus, DocumentType


class DocumentParcelAssociationRequest(BaseModel):
    parcel_id: str | None


class DocumentResponse(BaseModel):
    id: str
    parcel_id: str | None
    original_filename: str
    mime_type: str
    file_size_bytes: int = Field(ge=0)
    document_type: DocumentType
    status: DocumentStatus
    checksum_sha256: Annotated[str, Field(pattern=r"^[a-f0-9]{64}$")]
    created_at: datetime
    updated_at: datetime