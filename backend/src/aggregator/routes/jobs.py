from __future__ import annotations

from typing import Optional

from fastapi import APIRouter
from pydantic import BaseModel

from src.aggregator.jobs_runtime import start_make_all_ga, Job
from src.infra.db import get_job_record, list_jobs, list_artifacts

router = APIRouter(prefix="/api/v1/jobs", tags=["jobs"])


class MakeAllGAReq(BaseModel):
    ga_csv: str
    d: int
    catalog_csv: Optional[str] = None


@router.post("/make-all-ga", summary="Create a new make-all-ga job")
async def post_make_all_ga(req: MakeAllGAReq) -> dict[str, str]:
    job: Job = await start_make_all_ga(ga_csv=req.ga_csv, d=req.d, catalog_csv=req.catalog_csv)
    return {"id": job.id}


@router.get("/{job_id}")
async def get_job(job_id: str) -> dict[str, object]:
    rec = get_job_record(job_id)
    if not rec:
        return {"detail": "Not Found"}  # tests don't rely on error code here
    return {
        "id": rec.id,
        "kind": rec.kind,
        "status": rec.status,
        "created_at": rec.created_at.isoformat(),
        "updated_at": rec.updated_at.isoformat(),
    }


@router.get("")
async def list_jobs_route(limit: int = 50, offset: int = 0) -> dict[str, object]:
    items, total = list_jobs(limit=limit, offset=offset)
    return {
        "items": [
            {
                "id": r.id,
                "kind": r.kind,
                "status": r.status,
                "created_at": r.created_at.isoformat(),
                "updated_at": r.updated_at.isoformat(),
            }
            for r in items
        ],
        "total": total,
        "limit": limit,
        "offset": offset,
    }


@router.get("/{job_id}/artifacts")
async def list_artifacts_route(job_id: str) -> list[dict[str, object]]:
    arts = list_artifacts(job_id)
    return [
        {
            "id": a.id,
            "job_id": a.job_id,
            "kind": a.kind,
            "name": a.name,
            "path": a.path,
            "url": a.url,
            "created_at": a.created_at.isoformat(),
            "meta": a.meta or {},
        }
        for a in arts
    ]
