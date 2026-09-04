from datetime import datetime
from typing import Any

from pydantic import BaseModel, Field, model_validator

from app.models.parcel import ParcelStatus


class ParcelBase(BaseModel):
    khasra_number: str = Field(min_length=1)
    khata_number: str | None = None
    state: str = Field(min_length=1)
    district: str = Field(min_length=1)
    tehsil: str | None = None
    village: str = Field(min_length=1)
    recorded_area_m2: float = Field(gt=0)
    geometry: dict[str, Any]
    srid: int = Field(gt=0)
    confidence_score: float | None = Field(default=None, ge=0, le=1)

    @model_validator(mode="after")
    def require_polygon(self) -> "ParcelBase":
        if self.geometry.get("type") != "Polygon":
            raise ValueError("parcel geometry must be a GeoJSON Polygon")
        return self


class ParcelCreate(ParcelBase):
    id: str = Field(min_length=1, max_length=64)


class ParcelRead(ParcelBase):
    id: str
    status: ParcelStatus
    verification_status: str
    created_at: datetime
    updated_at: datetime

    model_config = {"from_attributes": True}


class ParcelListResponse(BaseModel):
    items: list[ParcelRead]
    total: int
    offset: int
    limit: int