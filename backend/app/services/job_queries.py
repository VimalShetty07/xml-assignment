import uuid
from datetime import UTC, datetime

from sqlalchemy import func, select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models import Job, Record, Task


def elapsed_seconds(
    started_at: datetime | None,
    finished_at: datetime | None,
) -> float | None:
    if started_at is None:
        return None
    end = finished_at if finished_at is not None else datetime.now(UTC)
    return (end - started_at).total_seconds()


async def task_status_counts(
    session: AsyncSession, job_id: uuid.UUID
) -> dict[str, int]:
    result = await session.execute(
        select(Task.status, func.count())
        .where(Task.job_id == job_id)
        .group_by(Task.status)
    )
    return {status: count for status, count in result.all()}


async def get_job_or_none(session: AsyncSession, job_id: uuid.UUID) -> Job | None:
    return await session.get(Job, job_id)


async def get_task_for_job_or_none(
    session: AsyncSession, job_id: uuid.UUID, task_id: uuid.UUID
) -> Task | None:
    result = await session.execute(
        select(Task).where(Task.id == task_id, Task.job_id == job_id)
    )
    return result.scalar_one_or_none()
