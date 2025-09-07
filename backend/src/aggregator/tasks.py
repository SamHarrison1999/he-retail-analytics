from __future__ import annotations

import os
from pathlib import Path
from typing import Optional

from src.infra.db import (
    append_job_log,
    record_artifact,
    update_job_status,
)


def _results_dir() -> Path:
    base = os.environ.get("RESULTS_DIR")
    return Path(base) if base else (Path.cwd() / "results")


def run_make_all_ga(job_id: str, ga_csv: str, d: int, catalog_csv: Optional[str]) -> None:
    """
    Minimal work used by tests:
    - mark job running
    - write results/<job_id>/hello.txt (artifact)
    - write results/figures/hello.txt (served via /files/figures/hello.txt)
    - record artifact
    - mark job succeeded
    """
    update_job_status(job_id, "running")
    append_job_log(job_id, f"start: ga_csv={ga_csv}, d={d}, catalog_csv={catalog_csv}")

    root = _results_dir()

    # Artifact file (per job)
    job_dir = root / job_id
    job_dir.mkdir(parents=True, exist_ok=True)
    hello_art = job_dir / "hello.txt"
    hello_art.write_text("demo artifact\n", encoding="utf-8")

    # Publicly served file expected by test
    fig_dir = root / "figures"
    fig_dir.mkdir(parents=True, exist_ok=True)
    hello_pub = fig_dir / "hello.txt"
    hello_pub.write_text("demo artifact\n", encoding="utf-8")

    record_artifact(
        job_id=job_id,
        kind="text",
        name="hello.txt",
        path=str(hello_art),
        url=None,
        meta={"note": "demo artifact"},
    )

    append_job_log(job_id, "done")
    update_job_status(job_id, "succeeded")
