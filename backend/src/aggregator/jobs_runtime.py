from __future__ import annotations

import asyncio
import json
import os
import sys
import uuid
from dataclasses import dataclass, field
from datetime import datetime, timezone
from pathlib import Path
from typing import AsyncIterator, Dict, List, Optional

from src.infra.db import (
    add_artifact,
    append_job_log,
    create_job_record,
    fetch_job_logs,
    update_job_status,
)


@dataclass
class Job:
    id: str
    kind: str
    status: str = "queued"
    created_at: str = field(default_factory=lambda: datetime.now(timezone.utc).isoformat())
    updated_at: str = field(default_factory=lambda: datetime.now(timezone.utc).isoformat())
    meta: dict = field(default_factory=dict)


class JobStore:
    """In-memory job index + pub/sub, with persistence in src.infra.db."""

    def __init__(self) -> None:
        self._jobs: Dict[str, Job] = {}
        self._subs: Dict[str, List[asyncio.Queue[str]]] = {}
        self._lock = asyncio.Lock()

    async def create(self, kind: str, meta: Optional[dict] = None) -> Job:
        jid = uuid.uuid4().hex
        now = datetime.now(timezone.utc)
        job = Job(id=jid, kind=kind, meta=meta or {})
        create_job_record(jid, kind, "queued", now, now)
        async with self._lock:
            self._jobs[jid] = job
            self._subs[jid] = []
        return job

    async def list(self) -> List[Job]:
        async with self._lock:
            return list(self._jobs.values())

    async def get(self, jid: str) -> Optional[Job]:
        async with self._lock:
            return self._jobs.get(jid)

    async def set_status(self, jid: str, status: str) -> None:
        update_job_status(jid, status)
        async with self._lock:
            if jid in self._jobs:
                self._jobs[jid].status = status
                self._jobs[jid].updated_at = datetime.now(timezone.utc).isoformat()

    async def append_log(self, jid: str, line: str) -> None:
        append_job_log(jid, line)
        async with self._lock:
            for q in self._subs.get(jid, []):
                await q.put(json.dumps({"line": line}))

    async def progress(self, jid: str, p: float, msg: str = "") -> None:
        payload = json.dumps({"progress": float(p), "msg": msg})
        async with self._lock:
            for q in self._subs.get(jid, []):
                await q.put(payload)

    async def subscribe(self, jid: str) -> AsyncIterator[str]:
        # Replay recent logs first
        for row in fetch_job_logs(jid, limit=1000):
            yield json.dumps({"line": row.line})

        q: asyncio.Queue[str] = asyncio.Queue()
        async with self._lock:
            self._subs.setdefault(jid, []).append(q)

        try:
            while True:
                item = await q.get()
                if item == '{"done": true}':
                    # forward sentinel then stop
                    yield item
                    break
                yield item
        finally:
            async with self._lock:
                subs = self._subs.get(jid, [])
                if q in subs:
                    subs.remove(q)

    async def close(self, jid: str) -> None:
        """Signal all subscribers to finish."""
        async with self._lock:
            for q in self._subs.get(jid, []):
                await q.put('{"done": true}')


STORE = JobStore()

# Resolve repo root and the CLI path
REPO_ROOT = Path(__file__).resolve().parents[3]  # .../repo/
HEPP_PATH = os.environ.get("HEPP_CLI", str(REPO_ROOT / "scripts" / "cli" / "hepp.py"))


def hepp_cmd(*cmd: str) -> List[str]:
    """Build a command to run the hepp CLI."""
    return [sys.executable, HEPP_PATH, *cmd]


async def run_cli_job(job: Job, args: List[str]) -> int:
    """Run a subprocess CLI job, streaming JSON progress/log lines to subscribers."""
    await STORE.set_status(job.id, "running")

    # Ensure the child process sees an absolute RESULTS_DIR, and run from repo root
    env = os.environ.copy()
    rd = env.get("RESULTS_DIR", "../results")
    env["RESULTS_DIR"] = str(Path(rd).resolve())

    proc = await asyncio.create_subprocess_exec(
        *args,
        stdout=asyncio.subprocess.PIPE,
        stderr=asyncio.subprocess.STDOUT,
        cwd=str(REPO_ROOT),
        env=env,
    )
    assert proc.stdout is not None

    try:
        async for raw in proc.stdout:
            line = raw.decode("utf-8", errors="replace").rstrip("\n")

            # Try to parse structured JSON messages first
            try:
                obj = json.loads(line)
                if isinstance(obj, dict):
                    if "progress" in obj:
                        await STORE.progress(job.id, float(obj["progress"]), obj.get("msg", ""))
                        continue
                    if "artifact" in obj:
                        a = obj["artifact"]
                        add_artifact(
                            job.id,
                            a.get("kind", "file"),
                            a.get("name", a.get("path", "artifact")),
                            a.get("path", ""),
                            a.get("sha256"),
                        )
                        await STORE.append_log(job.id, f"[artifact] {a.get('name','')} -> {a.get('path','')}")
                        continue
            except Exception:
                # Not JSON: treat it as a plain log line
                pass

            await STORE.append_log(job.id, line)

        rc = await proc.wait()
        await STORE.set_status(job.id, "succeeded" if rc == 0 else "failed")
        if rc == 0:
            await STORE.progress(job.id, 1.0, "Done")
        else:
            await STORE.append_log(job.id, f"[exit-code] {rc}")
        return rc
    finally:
        # Always tell subscribers to exit
        await STORE.close(job.id)


async def start_make_all_ga(ga_csv: str, d: int = 256, catalog_csv: Optional[str] = None) -> Job:
    """Kick off a demo 'make-all-ga' job (currently calls hepp demo)."""
    job = await STORE.create(kind="make-all-ga", meta={"ga_csv": ga_csv, "d": d, "catalog_csv": catalog_csv})
    asyncio.create_task(run_cli_job(job, hepp_cmd("demo")))
    return job
