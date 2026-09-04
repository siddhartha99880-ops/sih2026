from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from app.db.database import get_db
from app.repositories.infrastructure_repository import InfrastructureRepository
from app.schemas.infrastructure import InfrastructureCreate
from app.services.infrastructure_service import InfrastructureService


router = APIRouter(prefix="/infrastructure", tags=["infrastructure"])
service = InfrastructureService()


@router.post("", status_code=status.HTTP_201_CREATED)
def create_project(data: InfrastructureCreate, session: Session = Depends(get_db)):
    try:
        return service.to_read(service.create(session, data))
    except ValueError as exc:
        raise HTTPException(status_code=422, detail=str(exc)) from exc


@router.get("")
def list_projects(session: Session = Depends(get_db)):
    return [service.to_read(project) for project in service.repository.list(session)]


@router.get("/{project_id}")
def get_project(project_id: str, session: Session = Depends(get_db)):
    project = service.repository.get(session, project_id)
    if project is None:
        raise HTTPException(status_code=404, detail="infrastructure project not found")
    return service.to_read(project)


@router.put("/{project_id}")
def replace_project(project_id: str, data: InfrastructureCreate, session: Session = Depends(get_db)):
    if project_id != data.id:
        raise HTTPException(status_code=422, detail="path project_id must match body id")
    project = service.repository.get(session, project_id)
    if project is None:
        raise HTTPException(status_code=404, detail="infrastructure project not found")
    service.repository.delete(session, project)
    return service.to_read(service.create(session, data))


@router.delete("/{project_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_project(project_id: str, session: Session = Depends(get_db)) -> None:
    project = service.repository.get(session, project_id)
    if project is None:
        raise HTTPException(status_code=404, detail="infrastructure project not found")
    service.repository.delete(session, project)