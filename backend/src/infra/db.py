# backend/src/infra/db.py
from __future__ import annotations

import os
from contextlib import contextmanager
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Dict, Iterator, List, cast

from sqlalchemy import Column, JSON, and_, desc, select
from sqlalchemy.engine import Engine
from sqlalchemy.sql import Select
from sqlalchemy.sql.elements import ColumnElement
from sqlmodel import Field, Session, SQLModel, create_engine


# -------------------------
# Models
# -------------------------

class JobRecord(SQLModel, table=True):
    id: str = Field(primary_key=True)
    kind: str
    status: str
    created_at: datetime
    updated_at: datetime
    # explicit SQLAlchemy JSON column to keep pydantic/sqlalchemy happy
    meta: dict[str, Any] | None = Field(default=None, sa_column=Column(JSON))


class JobLog(SQLModel, table=True):
    id: int | None = Field(default=None, primary_key=True)
    job_id: str = Field(index=True)
    line: str
    created_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))


class Artifact(SQLModel, table=True):
    id: int | None = Field(default=None, primary_key=True)
    job_id: str = Field(index=True)
    kind: str
    name: str
    path: str
    sha256: str | None = None
    created_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))


# -------------------------
# Engine management
# -------------------------

_engine: Engine | None = None
_engine_url: str | None = None


def _default_sqlite_url() -> str:
    # repo-root/results/he.sqlite (API mounts ./results as /files)
    repo_root = Path(__file__).resolve().parents[3]
    results = repo_root / "results"
    results.mkdir(parents=True, exist_ok=True)
    return f"sqlite:///{results}/he.sqlite"


def ensure_engine(url: str | None) -> Engine:
    """
    Create tables and cache an Engine. If the requested URL differs from the
    current one, dispose the old engine and create a new one.
    """
    global _engine, _engine_url

    target_url = (url or "").strip() or _default_sqlite_url()

    # If SQLite file path, ensure parent directory exists
    if target_url.startswith("sqlite:///"):
        db_path = target_url.replace("sqlite:///", "", 1)
        Path(db_path).parent.mkdir(parents=True, exist_ok=True)

    if _engine is not None and _engine_url == target_url:
        return _engine

    # (Re)create engine
    connect_args: dict[str, Any] = {}
    if target_url.startswith("sqlite"):
        connect_args["check_same_thread"] = False

    _engine = create_engine(target_url, echo=False, connect_args=connect_args)
    _engine_url = target_url

    # First-time schema create (non-destructive for existing tables)
    SQLModel.metadata.create_all(_engine)
    return _engine


@contextmanager
def get_session() -> Iterator[Session]:
    if _engine is None:
        ensure_engine(os.environ.get("DB_URL"))
    assert _engine is not None
    with Session(_engine) as s:
        yield s


# -------------------------
# Job helpers (CRUD)
# -------------------------

def create_job_record(
    job_id: str,
    kind: str,
    status: str,
    created_at: datetime | None = None,
    meta: Dict[str, Any] | None = None,
) -> None:
    now = datetime.now(timezone.utc)
    jr = JobRecord(
        id=job_id,
        kind=kind,
        status=status,
        created_at=created_at or now,
        updated_at=now,
        meta=meta or None,
    )
    with get_session() as s:
        s.add(jr)
        s.commit()


def update_job_status(job_id: str, status: str) -> None:
    with get_session() as s:
        row = s.get(JobRecord, job_id)
        if not row:
            return
        row.status = status
        row.updated_at = datetime.now(timezone.utc)
        s.add(row)
        s.commit()


def append_job_log(job_id: str, line: str) -> None:
    with get_session() as s:
        s.add(JobLog(job_id=job_id, line=line))
        s.commit()


def add_artifact(job_id: str, kind: str, name: str, path: str, sha256: str | None = None) -> None:
    with get_session() as s:
        s.add(Artifact(job_id=job_id, kind=kind, name=name, path=path, sha256=sha256))
        s.commit()


def get_job_logs(job_id: str, limit: int = 100) -> List[JobLog]:
  """Newest first in DB; we reverse to return oldest->newest like a log tail."""
  with get_session() as s:
    jl_job_id: ColumnElement[str] = cast(Any, JobLog.__table__.c.job_id)  # type: ignore[attr-defined]
    jl_created: ColumnElement[datetime] = cast(Any, JobLog.__table__.c.created_at)  # type: ignore[attr-defined]

    q: Select[tuple[JobLog]] = (
      select(JobLog)
      .where(jl_job_id == job_id)
      .order_by(desc(jl_created))
      .limit(limit)
    )
    # SQLModel's typing for Session.exec doesn't fully line up with SA2 generics.
    result = s.exec(cast(Any, q))
    rows: List[JobLog] = list(result.scalars().all())
    rows.reverse()
    return rows


def list_artifacts(job_id: str) -> List[Artifact]:
  with get_session() as s:
    a_id: ColumnElement[int] = cast(Any, Artifact.__table__.c.id)  # type: ignore[attr-defined]
    a_job_id: ColumnElement[str] = cast(Any, Artifact.__table__.c.job_id)  # type: ignore[attr-defined]
    a_created: ColumnElement[datetime] = cast(Any, Artifact.__table__.c.created_at)  # type: ignore[attr-defined]

    q: Select[tuple[Artifact]] = (
      select(Artifact)
      .where(and_(a_job_id == job_id, a_id.is_not(None)))
      .order_by(desc(a_created))
      .limit(1000)
    )
    result = s.exec(cast(Any, q))
    return list(result.scalars().all())
