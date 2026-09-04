from fastapi import APIRouter
from pydantic import BaseModel

from app.core.config import get_settings
from app.db.database import database_ready


router = APIRouter(tags=["health"])


class HealthResponse(BaseModel):
    status: str
    environment: str
    database: str


@router.get("/health", response_model=HealthResponse)
def health() -> HealthResponse:
    ready = database_ready()
    return HealthResponse(
        status="ok" if ready else "degraded",
        environment=get_settings().app_env,
        database="ready" if ready else "unavailable",
    )