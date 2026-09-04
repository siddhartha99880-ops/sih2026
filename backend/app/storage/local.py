import hashlib
from dataclasses import dataclass
from pathlib import Path
from uuid import uuid4

from fastapi import UploadFile


ALLOWED_FILE_TYPES = {
    ".pdf": ("application/pdf", b"%PDF-"),
    ".jpg": ("image/jpeg", b"\xff\xd8\xff"),
    ".jpeg": ("image/jpeg", b"\xff\xd8\xff"),
    ".png": ("image/png", b"\x89PNG\r\n\x1a\n"),
}


@dataclass(frozen=True)
class StoredFile:
    stored_filename: str
    storage_path: str
    file_size_bytes: int
    checksum_sha256: str


class LocalDocumentStorage:
    def __init__(self, root: str | Path, max_size_bytes: int) -> None:
        self.root = Path(root)
        self.max_size_bytes = max_size_bytes

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
        suffix, _, signature = self.validate_upload(upload.filename, upload.content_type)
        stored_filename = f"{uuid4().hex}{suffix}"
        relative_path = Path("documents") / document_id / stored_filename
        destination = self.root / relative_path
        destination.parent.mkdir(parents=True, exist_ok=True)
        size = 0
        digest = hashlib.sha256()
        try:
            with destination.open("xb") as output:
                while chunk := upload.file.read(1024 * 1024):
                    size += len(chunk)
                    if size > self.max_size_bytes:
                        raise OverflowError("document exceeds the configured size limit")
                    digest.update(chunk)
                    output.write(chunk)
            with destination.open("rb") as saved_file:
                if saved_file.read(len(signature)) != signature:
                    raise ValueError("file content does not match its declared type")
        except Exception:
            destination.unlink(missing_ok=True)
            try:
                destination.parent.rmdir()
                self.root.joinpath("documents").rmdir()
            except OSError:
                pass
            raise
        return StoredFile(stored_filename, relative_path.as_posix(), size, digest.hexdigest())

    def path_for(self, storage_path: str) -> Path:
        relative = Path(storage_path)
        if relative.is_absolute() or ".." in relative.parts:
            raise ValueError("invalid storage path")
        candidate = (self.root / relative).resolve()
        root = self.root.resolve()
        if root not in candidate.parents:
            raise ValueError("invalid storage path")
        return candidate

    def delete(self, storage_path: str) -> None:
        file_path = self.path_for(storage_path)
        file_path.unlink(missing_ok=True)
        try:
            file_path.parent.rmdir()
            self.root.joinpath("documents").rmdir()
        except OSError:
            pass