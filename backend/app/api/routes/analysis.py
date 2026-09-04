from fastapi import APIRouter

from app.schemas.analysis import AnalysisRequest, AnalysisResponse
from app.services.analysis_service import AnalysisService


router = APIRouter(prefix="/analyses", tags=["analysis"])
service = AnalysisService()


@router.post("", response_model=AnalysisResponse, status_code=200)
def analyze_parcel(request: AnalysisRequest) -> AnalysisResponse:
    return service.analyze(request)