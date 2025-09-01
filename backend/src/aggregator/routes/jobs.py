from __future__ import annotations

from typing import List, Optional
from datetime import datetime

from fastapi import APIRouter, HTTPException
from fastapi.responses import StreamingResponse
from pydantic import BaseModel

from src.aggregator.jobs_runtime import STORE, Job, start_make_all_ga
from src.infra.db import list_artifacts as db_list_artifacts

router = APIRouter(prefix="/api/v1/jobs", tags=["jobs"])


class JobModel(BaseModel):
    id: str
    kind: str
    status: str
    created_at: str
    updated_at: str
    meta: dict | None = None


def _iso(v: str | datetime) -> str:
    return v if isinstance(v, str) else v.isoformat()


def to_model(j: Job) -> JobModel:
    return JobModel(
        id=j.id,
        kind=j.kind,
        status=j.status,
        created_at=_iso(j.created_at),
        updated_at=_iso(j.updated_at),
        meta=j.meta or None,
    )


class MakeAllGARequest(BaseModel):
    ga_csv: str
    d: int = 256
    catalog_csv: Optional[str] = None


class ArtifactModel(BaseModel):
    id: int | None = None
    job_id: str | None = None
    kind: str
    name: str
    path: str
    sha256: str | None = None
    created_at: str | None = None


@router.get("", response_model=List[JobModel])
async def list_jobs():
    jobs = await STORE.list()
    jobs.sort(key=lambda j: j.created_at, reverse=True)
    return [to_model(j) for j in jobs]


@router.post("/make-all-ga", response_model=JobModel)
async def post_make_all_ga(req: MakeAllGARequest):
    j = await start_make_all_ga(ga_csv=req.ga_csv, d=req.d, catalog_csv=req.catalog_csv)
    return to_model(j)


@router.get("/{job_id}", response_model=JobModel)
async def get_job(job_id: str):
    j = await STORE.get(job_id)
    if not j:
        raise HTTPException(status_code=404, detail="job not found")
    return to_model(j)


@router.get("/{job_id}/stream")
async def stream_logs(job_id: str):
    j = await STORE.get(job_id)
    if not j:
        raise HTTPException(status_code=404, detail="job not found")

    async def gen():
        async for item in STORE.subscribe(job_id):
            yield f"data: {item}\n\n"

    return StreamingResponse(gen(), media_type="text/event-stream")


@router.get("/{job_id}/artifacts", response_model=list[ArtifactModel])
async def get_artifacts(job_id: str):
    rows = db_list_artifacts(job_id)
    out: list[ArtifactModel] = []
    for a in rows:
        out.append(
            ArtifactModel(
                id=a.id,
                job_id=a.job_id,
                kind=a.kind,
                name=a.name,
                path=str(getattr(a, "path", "")),
                sha256=a.sha256,
                created_at=a.created_at.isoformat() if getattr(a, "created_at", None) else None,
            )
        )
    return out
