from sqlalchemy import func, or_, select
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
    ) -> list[Parcel]:
        query = self._filtered_query(search, state, district, tehsil, village, status)
        query = query.order_by(Parcel.created_at, Parcel.id).offset(offset).limit(limit)
        return list(session.scalars(query))

    def count(
        self,
        session: Session,
        search: str | None = None,
        state: str | None = None,
        district: str | None = None,
        tehsil: str | None = None,
        village: str | None = None,
        status: str | None = None,
    ) -> int:
        query = self._filtered_query(search, state, district, tehsil, village, status)
        return session.scalar(select(func.count()).select_from(query.subquery())) or 0

    def list_all(self, session: Session) -> list[Parcel]:
        return list(session.scalars(select(Parcel).order_by(Parcel.created_at, Parcel.id)))

    @staticmethod
    def _filtered_query(
        search: str | None,
        state: str | None,
        district: str | None,
        tehsil: str | None,
        village: str | None,
        status: str | None,
    ):
        query = select(Parcel)
        if search:
            pattern = f"%{search}%"
            query = query.where(or_(Parcel.id.ilike(pattern), Parcel.khasra_number.ilike(pattern), Parcel.khata_number.ilike(pattern)))
        for field, value in ((Parcel.state, state), (Parcel.district, district), (Parcel.tehsil, tehsil), (Parcel.village, village), (Parcel.status, status)):
            if value is not None:
                query = query.where(field == value)
        return query

    def delete(self, session: Session, parcel: Parcel) -> None:
        session.delete(parcel)
        session.commit()