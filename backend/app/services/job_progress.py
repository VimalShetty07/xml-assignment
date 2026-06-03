import json
import uuid
from datetime import UTC, datetime
from typing import Any

from sqlalchemy import select, update
from sqlalchemy.ext.asyncio import AsyncSession

from app.models import Job, Task
from app.services.job_queries import task_status_counts


def job_channel(job_id: uuid.UUID) -> str:
    return f"job:{job_id}"


async def increment_job_completed(session: AsyncSession, job_id: uuid.UUID) -> None:
    await session.execute(
        update(Job).where(Job.id == job_id).values(completed=Job.completed + 1)
    )


async def increment_job_failed(session: AsyncSession, job_id: uuid.UUID) -> None:
    await session.execute(
        update(Job).where(Job.id == job_id).values(failed=Job.failed + 1)
    )


async def finalize_job_if_done(
    session: AsyncSession, job_id: uuid.UUID
) -> tuple[Job, bool]:
    """Return (job, True) when the job just transitioned to a terminal state."""
    result = await session.execute(select(Job).where(Job.id == job_id))
    job = result.scalar_one()
    counts = await task_status_counts(session, job_id)

    job.completed = counts.get("completed", 0)
    job.failed = counts.get("failed", 0)

    pending = counts.get("pending", 0)
    in_progress = counts.get("in_progress", 0)
    if pending > 0 or in_progress > 0:
        return job, False
    if job.completed + job.failed < job.total:
        return job, False
    if job.finished_at is not None:
        return job, False
    job.finished_at = datetime.now(UTC)
    job.status = "failed" if job.failed == job.total else "completed"
    return job, True


def progress_payload(
    job: Job,
    task: Task,
    *,
    in_progress: int = 0,
    pending: int = 0,
    completed: int | None = None,
    failed: int | None = None,
) -> dict[str, Any]:
    return {
        "job_id": str(job.id),
        "task_id": str(task.id),
        "task_status": task.status,
        "job_status": job.status,
        "completed": completed if completed is not None else job.completed,
        "failed": failed if failed is not None else job.failed,
        "total": job.total,
        "in_progress": in_progress,
        "pending": pending,
        "records_count": task.records_count,
        "finished_at": job.finished_at.isoformat() if job.finished_at else None,
    }


async def publish_progress(
    redis: Any,
    job: Job,
    task: Task,
    *,
    in_progress: int = 0,
    pending: int = 0,
    completed: int | None = None,
    failed: int | None = None,
) -> None:
    payload = progress_payload(
        job,
        task,
        in_progress=in_progress,
        pending=pending,
        completed=completed,
        failed=failed,
    )
    await redis.publish(job_channel(job.id), json.dumps(payload))
