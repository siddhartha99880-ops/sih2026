from typing import Literal

from pydantic import BaseModel, Field


class ValidationFindingRead(BaseModel):
    code: str
    severity: Literal["PASS", "WARNING", "CONFLICT", "NEEDS_REVIEW"]
    message: str
    calculated_area_m2: float | None = None
    intersection_area_m2: float | None = None
    intersection_percentage: float | None = None


class OverlapResultRead(BaseModel):
    parcel_id: str
    overlap_area_m2: float
    overlap_percentage: float


class ValidationResponse(BaseModel):
    parcel_id: str
    geometry_valid: bool
    calculated_area_m2: float | None = None
    recorded_area_m2: float | None = None
    area_difference_m2: float | None = None
    area_difference_percent: float | None = None
    overlap_detected: bool
    overlapping_parcel_ids: list[str]
    overlap_results: list[OverlapResultRead]
    result: Literal["PASS", "WARNING", "CONFLICT", "NEEDS_REVIEW"]
    summary: str
    findings: list[ValidationFindingRead]
    overall_severity: Literal["PASS", "WARNING", "CONFLICT", "NEEDS_REVIEW"]