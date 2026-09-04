from logging.config import fileConfig

from alembic import context
from sqlalchemy import engine_from_config, pool

from app.db.database import Base
from app.db import models  # noqa: F401
from app.core.config import get_settings


config = context.config
config.set_main_option("sqlalchemy.url", get_settings().database_url)
if config.config_file_name:
    fileConfig(config.config_file_name)

target_metadata = Base.metadata


def include_name(name, type_, parent_names):
    if type_ == "schema":
        return name not in {"tiger", "tiger_data", "topology"}
    if type_ == "table" and parent_names.get("schema_name") == "public":
        return name not in {"spatial_ref_sys"}
    return True


def include_object(object_, name, type_, reflected, compare_to):
    if type_ == "table" and reflected:
        if object_.schema in {"tiger", "tiger_data", "topology"}:
            return False
        if object_.schema == "public" and name == "spatial_ref_sys":
            return False
        if object_.schema is None and name not in target_metadata.tables:
            return False
    return True


def run_migrations_offline() -> None:
    context.configure(url=get_settings().database_url, target_metadata=target_metadata, include_schemas=True, include_name=include_name, include_object=include_object, literal_binds=True, dialect_opts={"paramstyle": "named"})
    with context.begin_transaction():
        context.run_migrations()


def run_migrations_online() -> None:
    connectable = engine_from_config(config.get_section(config.config_ini_section, {}), prefix="sqlalchemy.", poolclass=pool.NullPool)
    with connectable.connect() as connection:
        context.configure(connection=connection, target_metadata=target_metadata, include_schemas=True, include_name=include_name, include_object=include_object)
        with context.begin_transaction():
            context.run_migrations()


if context.is_offline_mode():
    run_migrations_offline()
else:
    run_migrations_online()