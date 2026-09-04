from geoalchemy2.shape import from_shape, to_shape
from shapely.geometry import shape
from sqlalchemy.orm import Session

from app.models.parcel import Parcel, ParcelStatus
from app.repositories.parcel_repository import ParcelRepository
from app.schemas.parcel import ParcelCreate
from app.schemas.parcel import ParcelRead
from app.schemas.parcel import ParcelListResponse
from app.gis.geometry import geometry_to_geojson


class ParcelService:
    def __init__(self, repository: ParcelRepository | None = None) -> None:
        self.repository = repository or ParcelRepository()

    def create(self, session: Session, data: ParcelCreate) -> Parcel:
        geometry = shape(data.geometry)
        if not geometry.is_valid:
            raise ValueError("parcel geometry is invalid")
        parcel = Parcel(
            id=data.id, khasra_number=data.khasra_number, khata_number=data.khata_number,
            state=data.state, district=data.district, tehsil=data.tehsil, village=data.village,
            recorded_area_m2=data.recorded_area_m2, geometry=from_shape(geometry, srid=data.srid),
            srid=data.srid, status=ParcelStatus.UPLOADED, confidence_score=data.confidence_score,
        )
        return self.repository.create(session, parcel)

    @staticmethod
    def to_read(parcel: Parcel) -> ParcelRead:
        return ParcelRead(
            id=parcel.id, khasra_number=parcel.khasra_number, khata_number=parcel.khata_number,
            state=parcel.state, district=parcel.district, tehsil=parcel.tehsil, village=parcel.village,
            recorded_area_m2=parcel.recorded_area_m2, geometry=geometry_to_geojson(to_shape(parcel.geometry)),
            srid=parcel.srid, confidence_score=parcel.confidence_score, status=parcel.status,
            verification_status=parcel.verification_status, created_at=parcel.created_at, updated_at=parcel.updated_at,
        )

    def list(
        self,
        session: Session,
        search: str | None = None,
        state: str | None = None,
        district: str | None = None,
        tehsil: str | None = None,
        village: str | None = None,
        status: str | None = None,
        offset: int = 0,
        limit: int = 50,
    ) -> ParcelListResponse:
        parcels = self.repository.list(session, search, state, district, tehsil, village, status, offset, limit)
        total = self.repository.count(session, search, state, district, tehsil, village, status)
        return ParcelListResponse(items=[self.to_read(parcel) for parcel in parcels], total=total, offset=offset, limit=limit)