"""Create the initial PostGIS parcel and infrastructure schema."""

from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql
from geoalchemy2 import Geometry


revision = "0001_initial_postgis"
down_revision = None
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.execute("CREATE EXTENSION IF NOT EXISTS postgis")
    parcel_status = postgresql.ENUM("UPLOADED", "PROCESSING", "EXTRACTED", "NEEDS_REVIEW", "VERIFIED", "CONFLICT", "RESOLVED", name="parcelstatus", create_type=False)
    project_type = postgresql.ENUM("HIGHWAY", "RAILWAY", "CANAL", "PIPELINE", "TRANSMISSION_LINE", "OTHER", name="projecttype", create_type=False)
    validation_severity = postgresql.ENUM("PASS", "WARNING", "CONFLICT", "NEEDS_REVIEW", name="validationseverity", create_type=False)
    parcel_status.create(op.get_bind(), checkfirst=True)
    project_type.create(op.get_bind(), checkfirst=True)
    validation_severity.create(op.get_bind(), checkfirst=True)
    op.create_table(
        "parcels",
        sa.Column("id", sa.String(64), primary_key=True),
        sa.Column("khasra_number", sa.String(100), nullable=False),
        sa.Column("khata_number", sa.String(100)),
        sa.Column("state", sa.String(100), nullable=False),
        sa.Column("district", sa.String(100), nullable=False),
        sa.Column("tehsil", sa.String(100)),
        sa.Column("village", sa.String(100), nullable=False),
        sa.Column("recorded_area_m2", sa.Float, nullable=False),
        sa.Column("geometry", Geometry("POLYGON"), nullable=False),
        sa.Column("srid", sa.Integer, nullable=False, server_default="3857"),
        sa.Column("status", parcel_status, nullable=False),
        sa.Column("confidence_score", sa.Float),
        sa.Column("verification_status", sa.String(32), nullable=False, server_default="PENDING"),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
        sa.Column("updated_at", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
    )
    op.create_index("ix_parcels_khasra_number", "parcels", ["khasra_number"])
    op.create_table(
        "ownership_records",
        sa.Column("id", sa.Integer, primary_key=True),
        sa.Column("parcel_id", sa.String(64), sa.ForeignKey("parcels.id", ondelete="CASCADE"), nullable=False),
        sa.Column("owner_name", sa.String(200), nullable=False),
        sa.Column("share", sa.Float, nullable=False, server_default="1.0"),
    )
    op.create_index("ix_ownership_records_parcel_id", "ownership_records", ["parcel_id"])
    op.create_table(
        "infrastructure_projects",
        sa.Column("id", sa.String(64), primary_key=True),
        sa.Column("name", sa.String(200), nullable=False),
        sa.Column("project_type", project_type, nullable=False),
        sa.Column("status", sa.String(64), nullable=False, server_default="PLANNED"),
        sa.Column("corridor_geometry", Geometry("LINESTRING"), nullable=False),
        sa.Column("srid", sa.Integer, nullable=False, server_default="3857"),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
        sa.Column("updated_at", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
    )
    op.create_table(
        "validation_results",
        sa.Column("id", sa.Integer, primary_key=True),
        sa.Column("parcel_id", sa.String(64), sa.ForeignKey("parcels.id", ondelete="CASCADE"), nullable=False),
        sa.Column("code", sa.String(64), nullable=False),
        sa.Column("severity", validation_severity, nullable=False),
        sa.Column("message", sa.Text, nullable=False),
        sa.Column("calculated_area_m2", sa.Float),
        sa.Column("intersection_area_m2", sa.Float),
        sa.Column("intersection_percentage", sa.Float),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
    )
    op.create_index("ix_validation_results_parcel_id", "validation_results", ["parcel_id"])


def downgrade() -> None:
    op.drop_table("validation_results")
    op.drop_table("infrastructure_projects")
    op.drop_index("ix_ownership_records_parcel_id", table_name="ownership_records")
    op.drop_table("ownership_records")
    op.drop_index("ix_parcels_khasra_number", table_name="parcels")
    op.drop_table("parcels")
    sa.Enum(name="validationseverity").drop(op.get_bind(), checkfirst=True)
    sa.Enum(name="projecttype").drop(op.get_bind(), checkfirst=True)
    sa.Enum(name="parcelstatus").drop(op.get_bind(), checkfirst=True)