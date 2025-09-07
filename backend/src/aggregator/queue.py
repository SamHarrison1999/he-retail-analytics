from __future__ import annotations

import os
from typing import Any, Callable

from redis import Redis
from rq import Queue


def _redis() -> Redis:
    url = os.getenv("REDIS_URL", "redis://localhost:6379/0")
    return Redis.from_url(url)


def _queue() -> Queue:
    names = os.getenv("RQ_QUEUES", "default")
    name = [s.strip() for s in names.split(",") if s.strip()][0]
    return Queue(name, connection=_redis())


def enqueue(func: Callable[..., Any], *args: Any, **kwargs: Any):
    """
    Enqueue a callable onto the first queue in RQ_QUEUES (default 'default').
    """
    q = _queue()
    return q.enqueue(func, *args, **kwargs)
