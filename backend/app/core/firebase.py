import logging
from pathlib import Path
import firebase_admin
from firebase_admin import credentials, firestore, storage

logger = logging.getLogger(__name__)

PROJECT_ID = "h2026-b64c0"
STORAGE_BUCKET = "h2026-b64c0.firebasestorage.app"
CREDENTIALS_PATH = Path(__file__).resolve().parent.parent.parent / "service-account.json"

_firebase_app = None


def init_firebase():
    global _firebase_app
    if _firebase_app is not None:
        return _firebase_app
    if firebase_admin._apps:
        _firebase_app = firebase_admin.get_app()
        return _firebase_app

    if CREDENTIALS_PATH.exists():
        cred = credentials.Certificate(str(CREDENTIALS_PATH))
        _firebase_app = firebase_admin.initialize_app(cred, {
            "projectId": PROJECT_ID,
            "storageBucket": STORAGE_BUCKET,
        })
        logger.info("Firebase initialized successfully for project %s", PROJECT_ID)
    else:
        logger.warning("Firebase service-account.json not found at %s", CREDENTIALS_PATH)
    return _firebase_app


def get_firestore_client():
    init_firebase()
    return firestore.client()


def get_storage_bucket():
    init_firebase()
    return storage.bucket()


def is_firebase_ready() -> bool:
    try:
        app = init_firebase()
        return app is not None
    except Exception as exc:
        logger.warning("Firebase check failed: %s", exc)
        return False
