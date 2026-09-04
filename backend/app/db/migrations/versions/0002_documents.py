"""Create document metadata storage."""

from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql


revision = "0002_documents"
down_revision = "0001_initial_postgis"
branch_labels = None
depends_on = None


def upgrade() -> None:
    document_type = postgresql.ENUM(
        "LAND_DEED", "SALE_DEED", "KHATA", "KHASRA", "LAND_RECORD", "SURVEY_MAP", "OTHER", "UNKNOWN",
        name="documenttype", create_type=False,
    )
    document_status = postgresql.ENUM(
        "UPLOADED", "VALIDATED", "PROCESSING", "READY_FOR_OCR", "OCR_COMPLETE", "NEEDS_REVIEW", "FAILED",
        name="documentstatus", create_type=False,
    )
    document_type.create(op.get_bind(), checkfirst=True)
    document_status.create(op.get_bind(), checkfirst=True)
    op.create_table(
        "documents",
        sa.Column("id", sa.String(64), primary_key=True),
        sa.Column("parcel_id", sa.String(64), sa.ForeignKey("parcels.id", ondelete="SET NULL")),
        sa.Column("original_filename", sa.String(255), nullable=False),
        sa.Column("stored_filename", sa.String(255), nullable=False, unique=True),
        sa.Column("storage_path", sa.String(512), nullable=False, unique=True),
        sa.Column("mime_type", sa.String(100), nullable=False),
        sa.Column("file_size_bytes", sa.Integer, nullable=False),
        sa.Column("document_type", document_type, nullable=False),
        sa.Column("status", document_status, nullable=False),
        sa.Column("checksum_sha256", sa.String(64), nullable=False),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
        sa.Column("updated_at", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
    )
    op.create_index("ix_documents_parcel_id", "documents", ["parcel_id"])
    op.create_index("ix_documents_checksum_sha256", "documents", ["checksum_sha256"])
    op.create_index("ix_documents_status", "documents", ["status"])


def downgrade() -> None:
    op.drop_index("ix_documents_status", table_name="documents")
    op.drop_index("ix_documents_checksum_sha256", table_name="documents")
    op.drop_index("ix_documents_parcel_id", table_name="documents")
    op.drop_table("documents")
    sa.Enum(name="documentstatus").drop(op.get_bind(), checkfirst=True)
    sa.Enum(name="documenttype").drop(op.get_bind(), checkfirst=True)