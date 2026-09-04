from geoalchemy2.shape import from_shape
from shapely.geometry import shape
from sqlalchemy.orm import Session

from app.models.infrastructure import InfrastructureProject
from app.repositories.infrastructure_repository import InfrastructureRepository
from app.schemas.infrastructure import InfrastructureCreate
from app.schemas.infrastructure import InfrastructureRead
from app.gis.geometry import geometry_to_geojson
from geoalchemy2.shape import to_shape


class InfrastructureService:
    def __init__(self, repository: InfrastructureRepository | None = None) -> None:
        self.repository = repository or InfrastructureRepository()

    def create(self, session: Session, data: InfrastructureCreate) -> InfrastructureProject:
        geometry = shape(data.corridor_geometry)
        if not geometry.is_valid:
            raise ValueError("corridor geometry is invalid")
        project = InfrastructureProject(
            id=data.id, name=data.name, project_type=data.project_type, status=data.status,
            corridor_geometry=from_shape(geometry, srid=data.srid), srid=data.srid,
        )
        return self.repository.create(session, project)

    @staticmethod
    def to_read(project: InfrastructureProject) -> InfrastructureRead:
        return InfrastructureRead(
            id=project.id, name=project.name, project_type=project.project_type, status=project.status,
            corridor_geometry=geometry_to_geojson(to_shape(project.corridor_geometry)), srid=project.srid,
            created_at=project.created_at, updated_at=project.updated_at,
        )