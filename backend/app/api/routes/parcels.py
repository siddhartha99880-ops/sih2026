from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from app.db.database import get_db
from app.repositories.parcel_repository import ParcelRepository
from app.schemas.parcel import ParcelCreate
from app.services.parcel_service import ParcelService


router = APIRouter(prefix="/parcels", tags=["parcels"])
service = ParcelService()


@router.post("", status_code=status.HTTP_201_CREATED)
def create_parcel(data: ParcelCreate, session: Session = Depends(get_db)):
    try:
        return service.to_read(service.create(session, data))
    except ValueError as exc:
        raise HTTPException(status_code=422, detail=str(exc)) from exc


@router.get("")
def list_parcels(session: Session = Depends(get_db)):
    return [service.to_read(parcel) for parcel in service.repository.list(session)]


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