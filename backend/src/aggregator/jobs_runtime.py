from __future__ import annotations

import os
import secrets
from dataclasses import dataclass
from typing import Optional

from src.infra.db import create_job_record
from src.aggregator.tasks import run_make_all_ga


@dataclass
class Job:
    id: str
    kind: str


def _use_rq() -> bool:
    # Default to inline (tests expect synchronous completion)
    val = os.environ.get("USE_RQ", "").strip().lower()
    return val in {"1", "true", "yes"}


async def start_make_all_ga(ga_csv: str, d: int, catalog_csv: Optional[str]) -> Job:
    job_id = secrets.token_hex(16)
    kind = "make-all-ga"

    create_job_record(
        job_id=job_id,
        kind=kind,
        status="queued",
        meta={"ga_csv": ga_csv, "d": d, "catalog_csv": catalog_csv},
    )

    # For test env, run inline so status becomes "succeeded" quickly.
    # If you later wire RQ workers, branch on _use_rq().
    run_make_all_ga(job_id, ga_csv, d, catalog_csv)

    return Job(id=job_id, kind=kind)
