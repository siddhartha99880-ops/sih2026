import hashlib
from pathlib import Path
from uuid import uuid4

from fastapi import UploadFile

from app.core.firebase import get_storage_bucket
from app.storage.local import ALLOWED_FILE_TYPES, StoredFile


class FirebaseDocumentStorage:
    def __init__(self, max_size_bytes: int = 10 * 1024 * 1024) -> None:
        self.max_size_bytes = max_size_bytes

    def get_bucket(self):
        return get_storage_bucket()

    @staticmethod
    def validate_upload(filename: str | None, content_type: str | None) -> tuple[str, str, bytes]:
        if not filename:
            raise ValueError("file must have a filename")
        suffix = Path(filename).suffix.lower()
        file_type = ALLOWED_FILE_TYPES.get(suffix)
        if file_type is None:
            raise ValueError("unsupported document extension")
        expected_mime, signature = file_type
        if content_type != expected_mime:
            raise ValueError("unsupported document media type")
        return suffix, expected_mime, signature

    def save(self, upload: UploadFile, document_id: str) -> StoredFile:
        suffix, expected_mime, signature = self.validate_upload(upload.filename, upload.content_type)
        stored_filename = f"{uuid4().hex}{suffix}"
        cloud_path = f"documents/{document_id}/{stored_filename}"

        content = bytearray()
        digest = hashlib.sha256()

        while chunk := upload.file.read(1024 * 1024):
            content.extend(chunk)
            if len(content) > self.max_size_bytes:
                raise OverflowError("document exceeds the configured size limit")
            digest.update(chunk)

        if not content.startswith(signature):
            raise ValueError("file content does not match its declared type")

        bucket = self.get_bucket()
        blob = bucket.blob(cloud_path)
        blob.upload_from_string(bytes(content), content_type=expected_mime)

        storage_path = cloud_path

        return StoredFile(
            stored_filename=stored_filename,
            storage_path=storage_path,
            file_size_bytes=len(content),
            checksum_sha256=digest.hexdigest(),
        )

    def delete(self, storage_path: str) -> None:
        try:
            bucket = self.get_bucket()
            blob = bucket.blob(storage_path)
            if blob.exists():
                blob.delete()
        except Exception:
            pass
