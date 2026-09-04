from typing import Literal

from pydantic import BaseModel, Field


class ValidationFindingRead(BaseModel):
    code: str
    severity: Literal["PASS", "WARNING", "CONFLICT", "NEEDS_REVIEW"]
    message: str
    calculated_area_m2: float | None = None
    intersection_area_m2: float | None = None
    intersection_percentage: float | None = None


class ValidationResponse(BaseModel):
    parcel_id: str
    findings: list[ValidationFindingRead]
    overall_severity: Literal["PASS", "WARNING", "CONFLICT", "NEEDS_REVIEW"]