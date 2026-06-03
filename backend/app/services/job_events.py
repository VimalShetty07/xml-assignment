import json
import uuid
from collections.abc import AsyncIterator
from typing import Any

import redis.asyncio as aioredis
from fastapi import Request
from sqlalchemy.ext.asyncio import AsyncSession

from app.config import REDIS_URL
from app.models import Job
from app.services.job_progress import job_channel
from app.services.job_queries import task_status_counts


def snapshot_payload(job: Job, counts: dict[str, int]) -> dict[str, Any]:
    return {
        "event": "snapshot",
        "job_id": str(job.id),
        "job_status": job.status,
        "completed": counts.get("completed", 0),
        "failed": counts.get("failed", 0),
        "total": job.total,
        "in_progress": counts.get("in_progress", 0),
        "pending": counts.get("pending", 0),
        "finished_at": job.finished_at.isoformat() if job.finished_at else None,
    }


async def job_event_stream(
    request: Request,
    job_id: uuid.UUID,
    job: Job,
    db: AsyncSession,
) -> AsyncIterator[dict[str, str]]:
    counts = await task_status_counts(db, job_id)
    yield {"event": "snapshot", "data": json.dumps(snapshot_payload(job, counts))}

    if job.status in ("completed", "failed"):
        return

    client = aioredis.from_url(REDIS_URL, decode_responses=True)
    pubsub = client.pubsub()
    channel = job_channel(job_id)

    try:
        await pubsub.subscribe(channel)
        async for message in pubsub.listen():
            if await request.is_disconnected():
                break
            if message.get("type") != "message":
                continue

            data = message["data"]
            yield {"event": "progress", "data": data}

            try:
                payload = json.loads(data)
            except json.JSONDecodeError:
                continue
            if payload.get("job_status") in ("completed", "failed"):
                break
    finally:
        await pubsub.unsubscribe(channel)
        await pubsub.aclose()
        await client.aclose()
