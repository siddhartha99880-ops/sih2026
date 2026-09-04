from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.api.routes.health import router as health_router
from app.api.routes.analysis import router as analysis_router
from app.api.routes.infrastructure import router as infrastructure_router
from app.api.routes.parcels import router as parcels_router
from app.api.routes.validation import router as validation_router
from app.core.config import get_settings


settings = get_settings()
app = FastAPI(
    title="Land Intelligence Platform API",
    description="Prototype API for human-verified land digitization and infrastructure risk analysis.",
    version="0.1.0",
)
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.cors_origin_list,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)
app.include_router(health_router, prefix="/api/v1")
app.include_router(analysis_router, prefix="/api/v1")
app.include_router(parcels_router, prefix="/api/v1")
app.include_router(infrastructure_router, prefix="/api/v1")
app.include_router(validation_router, prefix="/api/v1")