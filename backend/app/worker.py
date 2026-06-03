import uuid
from datetime import UTC, datetime

from arq import Retry
from arq.connections import RedisSettings

from app.config import MAX_TASK_ATTEMPTS, REDIS_URL
from app.db import async_session
from app.logging_config import configure_logging, get_logger
from app.models import Job, Record, Task
from app.services.job_progress import (
    finalize_job_if_done,
    increment_job_completed,
    increment_job_failed,
    publish_progress,
)
from app.services.job_queries import task_status_counts
from app.services.retry import compute_backoff_seconds
from app.services.xml_feed import fetch_and_parse


async def process_task(ctx: dict, task_id: str) -> None:
    tid = uuid.UUID(task_id)

    async with async_session() as session:
        task = await session.get(Task, tid)
        if task is None:
            return
        if task.status in ("completed", "failed"):
            return
        job_id = task.job_id
        url = task.url
        task.status = "in_progress"
        task.attempts += 1
        task.updated_at = datetime.now(UTC)
        job = await session.get(Job, job_id)
        start_counts = await task_status_counts(session, job_id)
        await session.commit()

    await publish_progress(
        ctx["redis"],
        job,
        task,
        in_progress=start_counts.get("in_progress", 0),
        pending=start_counts.get("pending", 0),
        completed=start_counts.get("completed", 0),
        failed=start_counts.get("failed", 0),
    )

    log = get_logger(job_id=str(job_id), task_id=task_id)
    log.info("task_started", url=url, attempt=task.attempts)

    result = await fetch_and_parse(url)

    if not result.ok:
        log.warning(
            "fetch_failed",
            status=result.status_code,
            kind=result.error_kind,
            attempt=task.attempts,
            error=result.error,
        )

    counts = {"in_progress": 0, "pending": 0}
    job_finished = False
    async with async_session() as session:
        task = await session.get(Task, tid)
        if task is None or task.status in ("completed", "failed"):
            return

        if result.ok:
            session.add_all(
                [
                    Record(
                        task_id=tid,
                        title=r.title,
                        link=r.link,
                        published=r.published,
                        author=r.author,
                        summary=r.summary,
                    )
                    for r in result.records
                ]
            )
            task.status = "completed"
            task.records_count = len(result.records)
            task.time_taken_ms = result.elapsed_ms
            task.last_error = None
            task.error_kind = None
            await increment_job_completed(session, job_id)
        elif (
            result.error_kind == "transient"
            and task.attempts < MAX_TASK_ATTEMPTS
        ):
            task.status = "pending"
            task.last_error = result.error
            task.error_kind = result.error_kind
            task.time_taken_ms = result.elapsed_ms
            task.updated_at = datetime.now(UTC)
            await session.commit()
            defer = compute_backoff_seconds(
                task.attempts, result.retry_after_seconds
            )
            log.info(
                "task_retrying",
                kind=result.error_kind,
                attempt=task.attempts,
                defer_seconds=defer,
            )
            raise Retry(defer=defer)
        else:
            task.status = "failed"
            task.last_error = result.error
            task.error_kind = result.error_kind
            task.time_taken_ms = result.elapsed_ms
            task.records_count = 0
            await increment_job_failed(session, job_id)

        task.updated_at = datetime.now(UTC)
        job, job_finished = await finalize_job_if_done(session, job_id)
        counts = await task_status_counts(session, job_id)
        await session.commit()
        await session.refresh(task)
        await session.refresh(job)

    if result.ok:
        log.info(
            "task_completed",
            records=task.records_count,
            elapsed_ms=task.time_taken_ms,
        )
    else:
        log.info(
            "task_failed",
            kind=task.error_kind,
            attempt=task.attempts,
            elapsed_ms=task.time_taken_ms,
        )

    if job_finished:
        get_logger(job_id=str(job_id)).info(
            "job_completed",
            status=job.status,
            completed=job.completed,
            failed=job.failed,
            total=job.total,
        )

    await publish_progress(
        ctx["redis"],
        job,
        task,
        in_progress=counts.get("in_progress", 0),
        pending=counts.get("pending", 0),
        completed=counts.get("completed", 0),
        failed=counts.get("failed", 0),
    )


async def worker_startup(ctx: dict) -> None:
    configure_logging()
    get_logger().info("worker_started")


class WorkerSettings:
    functions = [process_task]
    redis_settings = RedisSettings.from_dsn(REDIS_URL)
    max_jobs = 15
    max_tries = MAX_TASK_ATTEMPTS
    on_startup = worker_startup
