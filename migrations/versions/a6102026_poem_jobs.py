"""Durable poem jobs and conversation ordering index."""

import sqlalchemy as sa
from alembic import op

revision = "a6102026"
down_revision = "80e25247c90a"
branch_labels = None
depends_on = None


def upgrade():
    op.create_table(
        "poem_job_gate",
        sa.Column("tenant_id", sa.String(128), primary_key=True),
        sa.Column("version", sa.Integer(), nullable=False),
    )
    op.create_table(
        "poem_jobs",
        sa.Column("tenant_id", sa.String(128), primary_key=True),
        sa.Column("job_id", sa.String(64), primary_key=True),
        sa.Column("idempotency_key", sa.String(128), nullable=False),
        sa.Column("payload", sa.Text(), nullable=False),
        sa.Column("model", sa.String(128), nullable=False),
        sa.Column("provider", sa.String(32), nullable=False),
        sa.Column("status", sa.String(32), nullable=False),
        sa.Column("created_at", sa.Float(), nullable=False),
        sa.Column("updated_at", sa.Float(), nullable=False),
        sa.Column("deadline", sa.Float(), nullable=False),
        sa.Column("lease_until", sa.Float(), nullable=False),
        sa.Column("owner", sa.String(64), nullable=False),
        sa.Column("progress", sa.Text(), nullable=False),
        sa.Column("result", sa.Text(), nullable=True),
        sa.Column("result_status", sa.Integer(), nullable=True),
        sa.Column("error", sa.Text(), nullable=True),
        sa.UniqueConstraint("tenant_id", "idempotency_key", name="uq_poem_job_key"),
    )
    op.create_index("ix_poem_jobs_claim", "poem_jobs", ["status", "lease_until", "created_at"])
    op.create_index(
        "ix_hoi_thoai_order", "hoi_thoai", ["tenant_id", "cap_nhat_luc", "conversation_id"]
    )


def downgrade():
    op.drop_index("ix_hoi_thoai_order", table_name="hoi_thoai")
    op.drop_table("poem_jobs")
    op.drop_table("poem_job_gate")
