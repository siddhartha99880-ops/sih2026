from typing import Literal

from pydantic import BaseModel, Field, model_validator


Point = tuple[float, float]
PolygonCoordinates = list[list[Point]]


class ExtractedFields(BaseModel):
    khasra_number: str = Field(min_length=1)
    owner_name: str = Field(min_length=1)
    recorded_area_m2: float = Field(gt=0)
    ownership_count: int = Field(default=1, ge=1)
    dispute_indicator: bool = False
    acquisition_stage_delay_days: int = Field(default=0, ge=0)


class PolygonInput(BaseModel):
    type: Literal["Polygon"] = "Polygon"
    srid: Literal[3857] = 3857
    coordinates: PolygonCoordinates

    @model_validator(mode="after")
    def has_closed_ring(self) -> "PolygonInput":
        if not self.coordinates or len(self.coordinates[0]) < 4:
            raise ValueError("polygon requires a closed ring with at least four points")
        if self.coordinates[0][0] != self.coordinates[0][-1]:
            raise ValueError("polygon ring must be closed")
        return self


class CorridorInput(BaseModel):
    type: Literal["LineString"] = "LineString"
    srid: Literal[3857] = 3857
    coordinates: list[Point] = Field(min_length=2)


class AnalysisRequest(BaseModel):
    parcel_id: str = Field(min_length=1)
    fields: ExtractedFields
    parcel: PolygonInput
    corridor: CorridorInput | None = None


class ValidationFinding(BaseModel):
    code: str
    severity: Literal["PASS", "WARNING", "CONFLICT"]
    message: str


class RiskFactor(BaseModel):
    factor: str
    impact: int = Field(ge=0)
    explanation: str


class RiskResult(BaseModel):
    score: int = Field(ge=0, le=100)
    level: Literal["LOW", "MEDIUM", "HIGH"]
    estimated_delay_days: int = Field(ge=0)
    factors: list[RiskFactor]


class AuditEvent(BaseModel):
    action: Literal["ANALYZED", "VERIFIED"]
    actor_id: str
    record_hash: str
    previous_hash: str | None = None


class AnalysisResponse(BaseModel):
    parcel_id: str
    calculated_area_m2: float
    area_difference_percent: float
    corridor_intersection_percent: float
    lifecycle_status: Literal["NEEDS_REVIEW", "CONFLICT"]
    findings: list[ValidationFinding]
    risk: RiskResult
    audit: AuditEvent