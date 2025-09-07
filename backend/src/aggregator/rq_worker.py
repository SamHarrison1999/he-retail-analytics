from __future__ import annotations

import os

from redis import Redis
from rq import Queue, Worker


def main() -> None:
    redis_url = os.getenv("REDIS_URL", "redis://localhost:6379/0")
    redis = Redis.from_url(redis_url)

    names = os.getenv("RQ_QUEUES", "default")
    queue_names = [s.strip() for s in names.split(",") if s.strip()] or ["default"]
    queues = [Queue(n, connection=redis) for n in queue_names]

    worker = Worker(queues, connection=redis)
    # with_scheduler=True keeps periodic cleanup and scheduled jobs working
    worker.work(with_scheduler=True)


if __name__ == "__main__":
    main()
