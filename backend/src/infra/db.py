from __future__ import annotations

import os
import hashlib
import datetime as dt
from pathlib import Path
from typing import Any, Optional, List, cast

from sqlalchemy import Column, desc
from sqlalchemy.engine import Engine
from sqlalchemy.sql import func
from sqlalchemy.sql.elements import ColumnElement
from sqlmodel import (
    Field,
    JSON,
    SQLModel,
    Session,
    create_engine,
    select,
)


# -------------------------
# Models
# -------------------------
class JobRecord(SQLModel, table=True):
    id: str = Field(primary_key=True, index=True)
    kind: str
    status: str
    created_at: dt.datetime
    updated_at: dt.datetime
    meta: Optional[dict[str, Any]] = Field(default=None, sa_column=Column(JSON))


class Artifact(SQLModel, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)
    job_id: str = Field(foreign_key="jobrecord.id", index=True)
    kind: str
    name: str
    path: Optional[str] = None
    url: Optional[str] = None
    created_at: dt.datetime
    meta: Optional[dict[str, Any]] = Field(default=None, sa_column=Column(JSON))


class JobLog(SQLModel, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)
    job_id: str = Field(foreign_key="jobrecord.id", index=True)
    ts: dt.datetime
    line: str


# -------------------------
# Engine / setup
# -------------------------
_engine: Optional[Engine] = None


def _default_db_url() -> str:
    results_dir = os.environ.get("RESULTS_DIR")
    base = Path(results_dir) if results_dir else (Path.cwd() / "results")
    base.mkdir(parents=True, exist_ok=True)
    return f"sqlite:///{base}/he.sqlite"


def ensure_engine(db_url: Optional[str] = None) -> Engine:
    global _engine
    if _engine is None:
        url = db_url or os.environ.get("DB_URL") or _default_db_url()
        _engine = create_engine(url, echo=False, future=True)
        SQLModel.metadata.create_all(_engine)
    return _engine


def create_tables() -> None:
    engine = ensure_engine()
    SQLModel.metadata.create_all(engine)


# -------------------------
# Job helpers
# -------------------------
def create_job_record(
    *,
    job_id: str,
    kind: str,
    status: str,
    meta: Optional[dict[str, Any]] = None,
) -> None:
    now = dt.datetime.now(dt.UTC)
    rec = JobRecord(
        id=job_id,
        kind=kind,
        status=status,
        created_at=now,
        updated_at=now,
        meta=meta or {},
    )
    engine = ensure_engine()
    with Session(engine) as s:
        s.add(rec)
        s.commit()


def update_job_status(job_id: str, status: str) -> None:
    engine = ensure_engine()
    with Session(engine) as s:
        rec = s.get(JobRecord, job_id)
        if rec is None:
            return
        rec.status = status
        rec.updated_at = dt.datetime.now(dt.UTC)
        s.add(rec)
        s.commit()


def append_job_log(job_id: str, line: str) -> None:
    engine = ensure_engine()
    with Session(engine) as s:
        s.add(JobLog(job_id=job_id, ts=dt.datetime.now(dt.UTC), line=line))
        s.commit()


def _sha256_file(path: Path) -> str:
    h = hashlib.sha256()
    with path.open("rb") as f:
        for chunk in iter(lambda: f.read(1024 * 1024), b""):
            h.update(chunk)
    return h.hexdigest()


def record_artifact(
    *,
    job_id: str,
    kind: str,
    name: str,
    path: Optional[str],
    url: Optional[str],
    meta: Optional[dict[str, Any]] = None,
) -> None:
    engine = ensure_engine()
    with Session(engine) as s:
        extra = dict(meta or {})
        if path:
            p = Path(path)
            if p.exists():
                extra.setdefault("sha256", _sha256_file(p))

        art = Artifact(
            job_id=job_id,
            kind=kind,
            name=name,
            path=path,
            url=url,
            created_at=dt.datetime.now(dt.UTC),
            meta=extra,
        )
        s.add(art)
        s.commit()


def get_job_record(job_id: str) -> Optional[JobRecord]:
    engine = ensure_engine()
    with Session(engine) as s:
        return s.get(JobRecord, job_id)


def list_artifacts(job_id: str) -> List[Artifact]:
    engine = ensure_engine()
    with Session(engine) as s:
        stmt = select(Artifact).where(Artifact.job_id == job_id)
        return list(s.exec(stmt).all())


def list_jobs(limit: int = 50, offset: int = 0) -> tuple[List[JobRecord], int]:
    engine = ensure_engine()
    with Session(engine) as s:
        # mypy: cast created_at to a SQL column element for desc()
        created_col = cast(ColumnElement[Any], JobRecord.created_at)

        items_stmt = (
            select(JobRecord)
            .order_by(desc(created_col))
            .limit(limit)
            .offset(offset)
        )
        items = list(s.exec(items_stmt).all())

        # Total count; cast to a tuple then index to satisfy mypy
        total_stmt = select(func.count()).select_from(JobRecord)
        row = cast(tuple[int], s.exec(total_stmt).one())
        total = int(row[0])

        return items, total