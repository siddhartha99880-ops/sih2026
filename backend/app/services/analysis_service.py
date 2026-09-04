import hashlib
import json
from dataclasses import dataclass

from shapely.geometry import LineString, Polygon

from app.schemas.analysis import (
    AnalysisRequest,
    AnalysisResponse,
    AuditEvent,
    RiskFactor,
    RiskResult,
    ValidationFinding,
)
from app.core.config import get_settings
from app.gis.intersection import corridor_intersection


@dataclass(frozen=True)
class AnalysisService:
    area_warning_percent: float = get_settings().area_warning_percent
    area_conflict_percent: float = get_settings().area_conflict_percent
    corridor_buffer_m: float = get_settings().corridor_buffer_m

    def analyze(self, request: AnalysisRequest, actor_id: str = "demo-verifier") -> AnalysisResponse:
        polygon = Polygon(request.parcel.coordinates[0])
        calculated_area = polygon.area
        difference_percent = abs(request.fields.recorded_area_m2 - calculated_area) / request.fields.recorded_area_m2 * 100
        findings = self._validation_findings(polygon.is_valid, difference_percent, request, calculated_area)
        corridor_percent = self._corridor_intersection_percent(polygon, request)
        if corridor_percent > 0:
            findings.append(ValidationFinding(
                code="SPATIAL_CONFLICT",
                severity="CONFLICT",
                message=f"Infrastructure corridor intersects {corridor_percent:.1f}% of the parcel.",
            ))
        risk = self._risk(difference_percent, corridor_percent, request)
        status = "CONFLICT" if any(f.severity == "CONFLICT" for f in findings) else "NEEDS_REVIEW"
        payload = {
            "parcel_id": request.parcel_id,
            "calculated_area_m2": round(calculated_area, 4),
            "area_difference_percent": round(difference_percent, 4),
            "corridor_intersection_percent": round(corridor_percent, 4),
            "findings": [finding.model_dump() for finding in findings],
            "risk": risk.model_dump(),
        }
        record_hash = hashlib.sha256(json.dumps(payload, sort_keys=True).encode()).hexdigest()
        return AnalysisResponse(
            **payload,
            lifecycle_status=status,
            audit=AuditEvent(action="ANALYZED", actor_id=actor_id, record_hash=record_hash),
        )

    def _validation_findings(self, is_valid: bool, difference_percent: float, request: AnalysisRequest, area: float) -> list[ValidationFinding]:
        findings = [ValidationFinding(
            code="GEOMETRY_VALID",
            severity="PASS" if is_valid else "CONFLICT",
            message="Parcel geometry is valid." if is_valid else "Parcel geometry is invalid and requires correction.",
        )]
        if difference_percent > self.area_conflict_percent:
            severity = "CONFLICT"
        elif difference_percent > self.area_warning_percent:
            severity = "WARNING"
        else:
            severity = "PASS"
        findings.append(ValidationFinding(
            code="AREA_COMPARISON",
            severity=severity,
            message=f"Recorded area is {request.fields.recorded_area_m2:.1f} m2; calculated area is {area:.1f} m2 ({difference_percent:.1f}% difference).",
        ))
        return findings

    @staticmethod
    def _corridor_intersection_percent(polygon: Polygon, request: AnalysisRequest) -> float:
        if request.corridor is None:
            return 0.0
        corridor = LineString(request.corridor.coordinates)
        return corridor_intersection(polygon, corridor, get_settings().corridor_buffer_m).percentage

    @staticmethod
    def _risk(difference_percent: float, corridor_percent: float, request: AnalysisRequest) -> RiskResult:
        factors: list[RiskFactor] = []
        if request.fields.ownership_count > 1:
            factors.append(RiskFactor(factor="ownership_complexity", impact=25, explanation="Multiple owners may require coordinated acquisition."))
        if request.fields.dispute_indicator:
            factors.append(RiskFactor(factor="dispute_indicator", impact=25, explanation="The source record is marked for legal or administrative review."))
        if difference_percent > 10:
            factors.append(RiskFactor(factor="area_mismatch", impact=20, explanation="Recorded and calculated parcel areas differ by more than 10%."))
        if corridor_percent > 0:
            factors.append(RiskFactor(factor="infrastructure_intersection", impact=20, explanation="The parcel intersects the supplied infrastructure corridor."))
        if request.fields.acquisition_stage_delay_days > 0:
            factors.append(RiskFactor(factor="acquisition_stage_delay", impact=10, explanation="The acquisition stage already has a reported delay."))
        score = min(100, sum(factor.impact for factor in factors))
        level = "HIGH" if score >= 60 else "MEDIUM" if score >= 30 else "LOW"
        return RiskResult(
            score=score,
            level=level,
            estimated_delay_days=request.fields.acquisition_stage_delay_days + (90 if level == "HIGH" else 30 if level == "MEDIUM" else 0),
            factors=factors,
        )