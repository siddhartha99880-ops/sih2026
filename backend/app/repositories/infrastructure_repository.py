from sqlalchemy import select
from sqlalchemy.orm import Session

from app.models.infrastructure import InfrastructureProject


class InfrastructureRepository:
    def create(self, session: Session, project: InfrastructureProject) -> InfrastructureProject:
        session.add(project)
        session.commit()
        session.refresh(project)
        return project

    def get(self, session: Session, project_id: str) -> InfrastructureProject | None:
        return session.scalar(select(InfrastructureProject).where(InfrastructureProject.id == project_id))

    def list(self, session: Session) -> list[InfrastructureProject]:
        return list(session.scalars(select(InfrastructureProject).order_by(InfrastructureProject.created_at)))

    def delete(self, session: Session, project: InfrastructureProject) -> None:
        session.delete(project)
        session.commit()