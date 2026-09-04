from datetime import datetime
from typing import Any

from pydantic import BaseModel, Field, model_validator

from app.models.infrastructure import ProjectType


class InfrastructureBase(BaseModel):
    name: str = Field(min_length=1)
    project_type: ProjectType
    status: str = Field(default="PLANNED", min_length=1)
    corridor_geometry: dict[str, Any]
    srid: int = Field(gt=0)

    @model_validator(mode="after")
    def require_line(self) -> "InfrastructureBase":
        if self.corridor_geometry.get("type") != "LineString":
            raise ValueError("corridor geometry must be a GeoJSON LineString")
        return self


class InfrastructureCreate(InfrastructureBase):
    id: str = Field(min_length=1, max_length=64)


class InfrastructureRead(InfrastructureBase):
    id: str
    created_at: datetime
    updated_at: datetime

    model_config = {"from_attributes": True}