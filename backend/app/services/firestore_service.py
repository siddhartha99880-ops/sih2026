import logging
from typing import Any
from app.core.firebase import get_firestore_client, is_firebase_ready

logger = logging.getLogger(__name__)


class FirestoreService:
    def __init__(self):
        self._db = None

    @property
    def db(self):
        if self._db is None:
            self._db = get_firestore_client()
        return self._db

    def sync_document(self, document_dict: dict[str, Any]) -> None:
        """Stores or updates document metadata in Firestore."""
        if not is_firebase_ready():
            return
        doc_id = document_dict.get("id")
        if doc_id:
            self.db.collection("documents").document(doc_id).set(document_dict, merge=True)
            logger.info("Synced document %s to Firestore", doc_id)

    def get_document(self, document_id: str) -> dict[str, Any] | None:
        if not is_firebase_ready():
            return None
        snapshot = self.db.collection("documents").document(document_id).get()
        return snapshot.to_dict() if snapshot.exists else None

    def list_documents(self) -> list[dict[str, Any]]:
        if not is_firebase_ready():
            return []
        docs = self.db.collection("documents").stream()
        return [doc.to_dict() for doc in docs]

    def sync_parcel(self, parcel_dict: dict[str, Any]) -> None:
        """Stores or updates parcel metadata in Firestore."""
        if not is_firebase_ready():
            return
        parcel_id = parcel_dict.get("id")
        if parcel_id:
            self.db.collection("parcels").document(parcel_id).set(parcel_dict, merge=True)
            logger.info("Synced parcel %s to Firestore", parcel_id)

    def list_parcels(self) -> list[dict[str, Any]]:
        if not is_firebase_ready():
            return []
        docs = self.db.collection("parcels").stream()
        return [doc.to_dict() for doc in docs]

    def record_validation(self, validation_dict: dict[str, Any]) -> None:
        """Records validation audit in Firestore."""
        if not is_firebase_ready():
            return
        val_id = validation_dict.get("id") or validation_dict.get("parcel_id")
        if val_id:
            self.db.collection("validations").document(val_id).set(validation_dict, merge=True)
            logger.info("Recorded validation for %s in Firestore", val_id)
