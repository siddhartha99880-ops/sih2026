from fastapi import APIRouter, Depends, Query
from geoalchemy2.shape import to_shape
from sqlalchemy.orm import Session

from app.db.database import get_db
from app.core.errors import ResourceNotFoundError
from app.gis.crs import transform_geometry
from app.repositories.parcel_repository import ParcelRepository
from app.repositories.infrastructure_repository import InfrastructureRepository
from app.services.validation_service import ValidationService


router = APIRouter(prefix="/validation", tags=["validation"])
parcel_repository = ParcelRepository()
infrastructure_repository = InfrastructureRepository()
validation_service = ValidationService()


@router.post("/parcel/{parcel_id}")
def validate_parcel(parcel_id: str, project_id: str | None = Query(default=None), session: Session = Depends(get_db)):
    parcel = parcel_repository.get(session, parcel_id)
    if parcel is None:
        raise ResourceNotFoundError(message="parcel not found")
    corridor = None
    if project_id is not None:
        project = infrastructure_repository.get(session, project_id)
        if project is None:
            raise ResourceNotFoundError(message="infrastructure project not found")
        corridor = to_shape(project.corridor_geometry)
        if project.srid != parcel.srid:
            corridor = transform_geometry(corridor, project.srid, parcel.srid)
    findings = validation_service.validate(parcel, corridor=corridor, other_parcels=parcel_repository.list_all(session))
    return findings