from sqlalchemy import select
from sqlalchemy.orm import Session

from app.models.parcel import Parcel


class ParcelRepository:
    def create(self, session: Session, parcel: Parcel) -> Parcel:
        session.add(parcel)
        session.commit()
        session.refresh(parcel)
        return parcel

    def get(self, session: Session, parcel_id: str) -> Parcel | None:
        return session.scalar(select(Parcel).where(Parcel.id == parcel_id))

    def list(self, session: Session) -> list[Parcel]:
        return list(session.scalars(select(Parcel).order_by(Parcel.created_at)))

    def delete(self, session: Session, parcel: Parcel) -> None:
        session.delete(parcel)
        session.commit()