import hashlib
from io import BytesIO

import pytest
from fastapi import UploadFile
from starlette.datastructures import Headers

from app.storage.local import LocalDocumentStorage


def upload(filename: str, content_type: str, content: bytes) -> UploadFile:
    return UploadFile(BytesIO(content), filename=filename, headers=Headers({"content-type": content_type}))


@pytest.mark.parametrize(
    ("filename", "content_type", "signature"),
    [
        ("deed.pdf", "application/pdf", b"%PDF-1.7 synthetic"),
        ("map.jpg", "image/jpeg", b"\xff\xd8\xff\xe0 synthetic"),
        ("map.jpeg", "image/jpeg", b"\xff\xd8\xff\xe0 synthetic"),
        ("map.png", "image/png", b"\x89PNG\r\n\x1a\n synthetic"),
    ],
)
def test_supported_files_are_stored_with_checksum(tmp_path, filename, content_type, signature) -> None:
    storage = LocalDocumentStorage(tmp_path, max_size_bytes=1024)
    stored = storage.save(upload(filename, content_type, signature), "DOCUMENT-1")

    destination = tmp_path / stored.storage_path
    assert destination.is_file()
    assert stored.storage_path == f"documents/DOCUMENT-1/{stored.stored_filename}"
    assert stored.file_size_bytes == len(signature)
    assert stored.checksum_sha256 == hashlib.sha256(signature).hexdigest()


def test_rejects_unsupported_type_mime_and_signature(tmp_path) -> None:
    storage = LocalDocumentStorage(tmp_path, max_size_bytes=1024)
    with pytest.raises(ValueError, match="extension"):
        storage.save(upload("notes.txt", "text/plain", b"text"), "DOCUMENT-1")
    with pytest.raises(ValueError, match="media type"):
        storage.save(upload("deed.pdf", "image/png", b"%PDF-1.7"), "DOCUMENT-2")
    with pytest.raises(ValueError, match="declared type"):
        storage.save(upload("deed.pdf", "application/pdf", b"not a pdf"), "DOCUMENT-3")


def test_rejects_oversized_file_and_cleans_partial_file(tmp_path) -> None:
    storage = LocalDocumentStorage(tmp_path, max_size_bytes=4)
    with pytest.raises(OverflowError):
        storage.save(upload("deed.pdf", "application/pdf", b"%PDF-12345"), "DOCUMENT-1")
    assert not list(tmp_path.rglob("*"))


def test_original_path_traversal_cannot_escape_storage_root(tmp_path) -> None:
    storage = LocalDocumentStorage(tmp_path, max_size_bytes=1024)
    stored = storage.save(upload("../../outside.pdf", "application/pdf", b"%PDF-1.7"), "DOCUMENT-1")
    assert stored.stored_filename != "../../outside.pdf"
    assert (tmp_path / stored.storage_path).resolve().parent == (tmp_path / "documents/DOCUMENT-1").resolve()
    with pytest.raises(ValueError):
        storage.path_for("../../outside.pdf")


def test_delete_is_idempotent(tmp_path) -> None:
    storage = LocalDocumentStorage(tmp_path, max_size_bytes=1024)
    stored = storage.save(upload("deed.pdf", "application/pdf", b"%PDF-1.7"), "DOCUMENT-1")
    storage.delete(stored.storage_path)
    storage.delete(stored.storage_path)
    assert not (tmp_path / stored.storage_path).exists()