# alembic/versions/0001_initial.py
from alembic import op
import sqlalchemy as sa

# If your file already has a generated revision id/filename, keep those.
revision = "0001_initial"
down_revision = None
branch_labels = None
depends_on = None


def upgrade():
    op.create_table(
        "jobrecord",
        sa.Column("id", sa.String(), primary_key=True, nullable=False),
        sa.Column("kind", sa.String(64), nullable=False),
        sa.Column("status", sa.String(32), nullable=False),
        sa.Column("created_at", sa.DateTime(), nullable=False),
        sa.Column("updated_at", sa.DateTime(), nullable=False),
        sa.Column("meta", sa.JSON(), nullable=True),
    )

    op.create_table(
        "joblog",
        sa.Column("id", sa.Integer(), primary_key=True, autoincrement=True),
        sa.Column("job_id", sa.String(), nullable=False),
        sa.Column("line", sa.Text(), nullable=False),
        sa.Column("created_at", sa.DateTime(), nullable=False),
    )
    op.create_index("ix_joblog_job_id", "joblog", ["job_id"])

    op.create_table(
        "artifact",
        sa.Column("id", sa.Integer(), primary_key=True, autoincrement=True),
        sa.Column("job_id", sa.String(), nullable=False),
        sa.Column("kind", sa.String(32), nullable=False),
        sa.Column("name", sa.String(256), nullable=False),
        sa.Column("path", sa.String(1024), nullable=False),
        sa.Column("created_at", sa.DateTime(), nullable=False),
        sa.Column("sha256", sa.String(length=64), nullable=True),
    )
    op.create_index("ix_artifact_job_id", "artifact", ["job_id"])


def downgrade():
    op.drop_index("ix_artifact_job_id", table_name="artifact")
    op.drop_table("artifact")
    op.drop_index("ix_joblog_job_id", table_name="joblog")
    op.drop_table("joblog")
    op.drop_table("jobrecord")
