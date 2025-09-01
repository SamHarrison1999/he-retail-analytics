from __future__ import annotations

import os
from contextlib import contextmanager
from datetime import datetime, timezone
from typing import Any, Generator, Optional, cast

from sqlalchemy import JSON, Column, and_, desc
from sqlalchemy.engine import Engine
from sqlalchemy.sql.elements import ColumnElement
from sqlmodel import Field, Session, SQLModel, create_engine, select


# =========================
# Models
# =========================

class JobRun(SQLModel, table=True):
    id: str = Field(primary_key=True)
    kind: str
    status: str
    created_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))
    updated_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))
    meta: Optional[dict] = Field(default=None, sa_column=Column(JSON))


class JobLog(SQLModel, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)
    job_id: str = Field(index=True)
    line: str
    created_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))


class Artifact(SQLModel, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)
    job_id: str = Field(index=True)
    kind: str
    name: str
    path: str
    sha256: Optional[str] = None
    created_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))


# =========================
# Engine / sessions
# =========================

_ENGINE: Engine | None = None


def _mkdir_for_sqlite(url: str) -> None:
    if not url.startswith("sqlite:///"):
        return
    sqlite_path: str = os.path.abspath(url[len("sqlite:///") :])
    sqlite_dir: str = os.path.dirname(sqlite_path)
    if sqlite_dir:
        os.makedirs(sqlite_dir, exist_ok=True)


def ensure_engine(db_url: str | None = None) -> Engine:
    global _ENGINE
    if _ENGINE is not None:
        return _ENGINE

    url: str = db_url or os.environ.get("DB_URL") or "sqlite:///../results/he.sqlite"
    _mkdir_for_sqlite(url)
    _ENGINE = create_engine(url, echo=False, future=True)
    SQLModel.metadata.create_all(_ENGINE)
    return _ENGINE


@contextmanager
def get_session() -> Generator[Session, None, None]:
    engine = ensure_engine()
    with Session(engine) as s:
        yield s


# =========================
# CRUD helpers
# =========================

def create_job(job_id: str, kind: str, status: str, meta: dict | None = None) -> None:
    with get_session() as s:
        now = datetime.now(timezone.utc)
        jr = JobRun(
            id=job_id,
            kind=kind,
            status=status,
            meta=meta,
            created_at=now,
            updated_at=now,
        )
        s.add(jr)
        s.commit()


def update_job_status(job_id: str, status: str) -> None:
    with get_session() as s:
        jr = s.get(JobRun, job_id)
        if jr is None:
            jr = JobRun(id=job_id, kind="unknown", status=status)
            s.add(jr)
        else:
            jr.status = status
            jr.updated_at = datetime.now(timezone.utc)
            s.add(jr)
        s.commit()


def append_job_log(job_id: str, line: str) -> None:
    with get_session() as s:
        s.add(JobLog(job_id=job_id, line=line))
        s.commit()


def get_job_logs(job_id: str, limit: int = 200) -> list[JobLog]:
    """
    Return logs ordered oldest→newest.
    Use sqlmodel.select(...) so Session.exec(...) returns ScalarResult[JobLog],
    which mypy understands.
    """
    with get_session() as s:
        cond: ColumnElement[bool] = cast(ColumnElement[bool], JobLog.job_id == job_id)
        created_col: ColumnElement[Any] = cast(ColumnElement[Any], JobLog.created_at)

        q = (
            select(JobLog)                # <- sqlmodel.select
            .where(and_(cond))
            .order_by(desc(created_col))
            .limit(limit)
        )
        rows: list[JobLog] = list(s.exec(q).all())
        rows.reverse()  # newest→oldest -> oldest→newest
        return rows


def add_artifact(
    job_id: str,
    kind: str,
    name: str,
    path: str,
    sha256: str | None = None,
) -> Artifact:
    art = Artifact(job_id=job_id, kind=kind, name=name, path=path, sha256=sha256)
    with get_session() as s:
        s.add(art)
        s.commit()
        s.refresh(art)
    return art


def list_artifacts(job_id: str) -> list[Artifact]:
    with get_session() as s:
        cond: ColumnElement[bool] = cast(ColumnElement[bool], Artifact.job_id == job_id)
        created_col: ColumnElement[Any] = cast(ColumnElement[Any], Artifact.created_at)

        q = (
            select(Artifact)              # <- sqlmodel.select
            .where(and_(cond))
            .order_by(created_col)        # oldest→newest
        )
        return list(s.exec(q).all())


# =========================
# Backwards-compat shims
# =========================

def create_job_record(
    job_id: str,
    kind: str,
    status: str,
    created_at: datetime | None = None,
    meta: dict | None = None,
) -> None:
    # We ignore created_at because the model has defaults; keep for compatibility.
    _ = created_at
    create_job(job_id=job_id, kind=kind, status=status, meta=meta)


def fetch_job_logs(job_id: str, limit: int = 200) -> list[JobLog]:
    return get_job_logs(job_id=job_id, limit=limit)


__all__ = [
    "JobRun",
    "JobLog",
    "Artifact",
    "ensure_engine",
    "get_session",
    "create_job",
    "create_job_record",
    "update_job_status",
    "append_job_log",
    "get_job_logs",
    "fetch_job_logs",
    "add_artifact",
    "list_artifacts",
]
