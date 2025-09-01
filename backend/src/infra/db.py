from __future__ import annotations
from typing import Optional, List
from datetime import datetime, timezone
from sqlmodel import SQLModel, Field, create_engine, Session, select
from sqlalchemy.engine import make_url
import os

class JobRecord(SQLModel, table=True):
    id: str = Field(primary_key=True)
    kind: str
    status: str
    created_at: datetime
    updated_at: datetime

class JobLog(SQLModel, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)
    job_id: str = Field(index=True)
    line: str
    ts: datetime

class Artifact(SQLModel, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)
    job_id: str = Field(index=True)
    kind: str
    name: str
    path: str
    sha256: Optional[str] = None
    created_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))

_engine = None


def ensure_engine(db_url: str | None):
    """Init engine + create tables once. Ensures SQLite parent dir exists."""
    global _engine
    if _engine is not None:
      return

    results_dir = os.environ.get("RESULTS_DIR", "../results")
    url_str = db_url or f"sqlite:///{results_dir}/he.sqlite"

    # If using SQLite, create the directory if needed
    try:
      url = make_url(url_str)
      if url.drivername.startswith("sqlite") and url.database not in (None, "", ":memory:"):
        os.makedirs(os.path.dirname(url.database), exist_ok=True)
    except Exception:
      # Non-SQLite URLs or malformed URLs: just continue
      pass

    _engine = create_engine(url_str, echo=False, future=True)
    SQLModel.metadata.create_all(_engine)

def get_session() -> Session:
    assert _engine is not None, "DB not initialized; call ensure_engine() first."
    return Session(_engine)

def create_job_record(job_id: str, kind: str, status: str, created_at: datetime, updated_at: datetime):
    with get_session() as s:
        s.add(JobRecord(id=job_id, kind=kind, status=status, created_at=created_at, updated_at=updated_at))
        s.commit()

def update_job_status(job_id: str, status: str):
    with get_session() as s:
        jr = s.get(JobRecord, job_id)
        if jr:
            jr.status = status
            jr.updated_at = datetime.now(timezone.utc)
            s.add(jr); s.commit()

def append_job_log(job_id: str, line: str):
    with get_session() as s:
        s.add(JobLog(job_id=job_id, line=line, ts=datetime.now(timezone.utc)))
        s.commit()

def fetch_job_logs(job_id: str, limit: int = 1000) -> List[JobLog]:
    with get_session() as s:
        q = select(JobLog).where(JobLog.job_id == job_id).order_by(JobLog.id.desc()).limit(limit)
        rows = list(s.exec(q).all()); rows.reverse()
        return rows

def add_artifact(job_id: str, kind: str, name: str, path: str, sha256: str | None = None):
    with get_session() as s:
        s.add(Artifact(job_id=job_id, kind=kind, name=name, path=path, sha256=sha256))
        s.commit()

def list_artifacts(job_id: str) -> list[Artifact]:
    with get_session() as s:
        q = select(Artifact).where(Artifact.job_id == job_id).order_by(Artifact.id)
        return list(s.exec(q).all())
