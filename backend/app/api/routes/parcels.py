from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy.orm import Session

from app.db.database import get_db
from app.repositories.parcel_repository import ParcelRepository
from app.schemas.parcel import ParcelCreate
from app.schemas.parcel import ParcelListResponse
from app.services.parcel_service import ParcelService


router = APIRouter(prefix="/parcels", tags=["parcels"])
service = ParcelService()


@router.post("", status_code=status.HTTP_201_CREATED)
def create_parcel(data: ParcelCreate, session: Session = Depends(get_db)):
    try:
        return service.to_read(service.create(session, data))
    except ValueError as exc:
        raise HTTPException(status_code=422, detail=str(exc)) from exc


@router.get("", response_model=ParcelListResponse)
def list_parcels(
    search: str | None = Query(default=None, max_length=100),
    state: str | None = Query(default=None, max_length=100),
    district: str | None = Query(default=None, max_length=100),
    tehsil: str | None = Query(default=None, max_length=100),
    village: str | None = Query(default=None, max_length=100),
    status: str | None = Query(default=None, max_length=50),
    offset: int = Query(default=0, ge=0),
    limit: int = Query(default=50, ge=1, le=100),
    session: Session = Depends(get_db),
):
    return service.list(session, search, state, district, tehsil, village, status, offset, limit)


@router.get("/{parcel_id}")
def get_parcel(parcel_id: str, session: Session = Depends(get_db)):
    parcel = service.repository.get(session, parcel_id)
    if parcel is None:
        raise HTTPException(status_code=404, detail="parcel not found")
    return service.to_read(parcel)


@router.put("/{parcel_id}")
def replace_parcel(parcel_id: str, data: ParcelCreate, session: Session = Depends(get_db)):
    if parcel_id != data.id:
        raise HTTPException(status_code=422, detail="path parcel_id must match body id")
    parcel = service.repository.get(session, parcel_id)
    if parcel is None:
        raise HTTPException(status_code=404, detail="parcel not found")
    service.repository.delete(session, parcel)
    return service.to_read(service.create(session, data))


@router.delete("/{parcel_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_parcel(parcel_id: str, session: Session = Depends(get_db)) -> None:
    parcel = service.repository.get(session, parcel_id)
    if parcel is None:
        raise HTTPException(status_code=404, detail="parcel not found")
    service.repository.delete(session, parcel)