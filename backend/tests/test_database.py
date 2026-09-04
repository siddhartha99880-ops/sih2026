from app.db.database import Base, database_ready, engine
from app.db import models  # noqa: F401


def test_database_engine_uses_configured_postgres_url() -> None:
    assert engine.url.drivername == "postgresql+psycopg"


def test_database_models_are_registered() -> None:
    assert {"parcels", "ownership_records", "infrastructure_projects", "validation_results"} <= set(Base.metadata.tables)


def test_database_readiness_is_boolean() -> None:
    assert isinstance(database_ready(), bool)