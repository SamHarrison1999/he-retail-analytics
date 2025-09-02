from __future__ import annotations

import asyncio
import json
import os
from dataclasses import dataclass
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, AsyncIterator, Dict, List, Optional


from src.infra.db import (
    add_artifact,
    append_job_log,
    create_job_record,
    update_job_status,
)


# ---------- Models ----------

@dataclass
class Job:
    id: str
    kind: str
    status: str
    created_at: str
    updated_at: str
    meta: Dict[str, Any] | None = None


# ---------- In-memory async event store (publish/subscribe per job) ----------

class AsyncEventStore:
    def __init__(self) -> None:
        self._jobs: Dict[str, Job] = {}
        self._qs: Dict[str, asyncio.Queue[str]] = {}
        self._lock = asyncio.Lock()

    def _queue(self, job_id: str) -> asyncio.Queue[str]:
        if job_id not in self._qs:
            self._qs[job_id] = asyncio.Queue(maxsize=1000)
        return self._qs[job_id]

    async def publish(self, job_id: str, sse_json_line: str) -> None:
        await self._queue(job_id).put(sse_json_line)

    async def subscribe(self, job_id: str) -> AsyncIterator[str]:
        """
        Yields JSON strings that are already SSE-ready (caller wraps 'data: ...\\n\\n').
        Stops when an event contains {"done": true}.
        """
        q = self._queue(job_id)
        while True:
            item = await q.get()
            yield item
            try:
                obj = json.loads(item)
            except Exception:
                obj = {}
            if isinstance(obj, dict) and obj.get("done"):
                break

    async def list(self) -> List[Job]:
        async with self._lock:
            return list(self._jobs.values())

    async def get(self, job_id: str) -> Optional[Job]:
        async with self._lock:
            return self._jobs.get(job_id)

    async def put_job(self, job: Job) -> None:
        async with self._lock:
            self._jobs[job.id] = job

    async def update_job(self, job_id: str, **fields: Any) -> None:
        async with self._lock:
            j = self._jobs.get(job_id)
            if j:
                for k, v in fields.items():
                    setattr(j, k, v)  # ok for dataclass


STORE = AsyncEventStore()


# ---------- Job spec & helpers ----------

def _repo_root() -> Path:
    # backend/src/aggregator -> backend/src -> backend -> repo-root
    return Path(__file__).resolve().parents[3]


@dataclass
class JobSpec:
    args: List[str]
    env: Dict[str, str]


def _build_job_spec(kind: str, meta: Dict[str, Any]) -> JobSpec:
    # Route everything to the demo runner for now
    script = str(_repo_root() / "scripts" / "cli" / "hepp.py")
    args = ["python", script]
    env = os.environ.copy()
    return JobSpec(args=args, env=env)


async def _run_child_and_publish(job_id: str, kind: str, meta: Dict[str, Any]) -> None:
    """
    Spawn child process asynchronously, forward its JSON/plain lines to STORE,
    capture artifacts and progress, and update DB status.
    """
    spec = _build_job_spec(kind, meta)

    # Mark running in DB and in-memory
    update_job_status(job_id, "running")
    await STORE.update_job(job_id, status="running", updated_at=datetime.now(timezone.utc).isoformat())

    try:
        proc = await asyncio.create_subprocess_exec(
            *spec.args,
            cwd=str(_repo_root()),
            env=spec.env,
            stdout=asyncio.subprocess.PIPE,
            stderr=asyncio.subprocess.STDOUT,
        )
    except FileNotFoundError as e:
        append_job_log(job_id, f"spawn error: {e}")
        update_job_status(job_id, "failed")
        await STORE.publish(job_id, json.dumps({"line": f"spawn error: {e}"}))
        await STORE.publish(job_id, json.dumps({"done": True, "status": "failed"}))
        return

    stdout = proc.stdout
    assert stdout is not None  # mypy: stdout is Optional

    # Read lines until EOF
    while True:
        raw = await stdout.readline()
        if not raw:
            break

        text = raw.decode("utf-8", errors="replace").rstrip("\n")
        # Try JSON
        event: Dict[str, Any]
        try:
            event = json.loads(text)
        except Exception:
            # Plain line
            append_job_log(job_id, text)
            await STORE.publish(job_id, json.dumps({"line": text}))
            continue

        # Progress?
        if "progress" in event:
            msg = str(event.get("msg", "")).strip()
            if msg:
                append_job_log(job_id, f"[progress] {msg}")

        # Artifact?
        if "artifact" in event and isinstance(event["artifact"], dict):
            art = event["artifact"]
            add_artifact(
                job_id=job_id,
                kind=str(art.get("kind", "file")),
                name=str(art.get("name", "")),
                path=str(art.get("path", "")),
            )
            append_job_log(job_id, f"[artifact] {art.get('name','?')} -> {art.get('path','')}")
            # Also mirror a friendly line for simple clients
            await STORE.publish(
                job_id, json.dumps({"line": f"[artifact] {art.get('name','?')} -> {art.get('path','')}"})
            )

        # Forward the original event too
        await STORE.publish(job_id, json.dumps(event))

    rc = await proc.wait()
    final = "succeeded" if rc == 0 else "failed"
    update_job_status(job_id, final)
    await STORE.update_job(job_id, status=final, updated_at=datetime.now(timezone.utc).isoformat())
    await STORE.publish(job_id, json.dumps({"done": True, "status": final}))


# ---------- Public API used by routes ----------

async def start_make_all_ga(ga_csv: str, d: int = 256, catalog_csv: str | None = None) -> Job:
    """Create a job record, enqueue the async runner, and return the Job."""
    job_id = os.urandom(16).hex()
    now = datetime.now(timezone.utc).isoformat()
    kind = "make-all-ga"
    meta: Dict[str, Any] = {"ga_csv": ga_csv, "d": d, "catalog_csv": catalog_csv}

    # Persist initial record
    create_job_record(job_id=job_id, kind=kind, status="queued", created_at=datetime.fromisoformat(now), meta=meta)

    j = Job(id=job_id, kind=kind, status="queued", created_at=now, updated_at=now, meta=meta)
    await STORE.put_job(j)

    # Fire and forget the runner
    asyncio.create_task(_run_child_and_publish(job_id=job_id, kind=kind, meta=meta))
    return j