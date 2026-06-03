import asyncio
import uuid
from datetime import UTC, datetime

from arq import ArqRedis
from fastapi import APIRouter, Depends, HTTPException, Query, Request
from sqlalchemy import func, select
from sqlalchemy.ext.asyncio import AsyncSession
from sse_starlette.sse import EventSourceResponse

from app.db import get_db
from app.feeds import load_feed_urls
from app.logging_config import get_logger
from app.models import Job, Record, Task
from app.schemas import (
    JobCreatedResponse,
    JobDetailResponse,
    JobListResponse,
    JobSummary,
    RecordListResponse,
    RecordResponse,
    TaskDetailResponse,
    TaskListResponse,
    TaskStatusFilter,
    TaskSummary,
)
from app.services.job_events import job_event_stream
from app.services.job_progress import finalize_job_if_done
from app.services.job_queries import (
    elapsed_seconds,
    get_job_or_none,
    get_task_for_job_or_none,
    task_status_counts,
)

router = APIRouter(prefix="/jobs", tags=["jobs"])

JOBS_LIST_LIMIT = 50


def get_arq_pool(request: Request) -> ArqRedis:
    return request.app.state.arq_pool


@router.post("", response_model=JobCreatedResponse, status_code=201)
async def create_job(
    db: AsyncSession = Depends(get_db),
    arq_pool: ArqRedis = Depends(get_arq_pool),
) -> JobCreatedResponse:
    urls = load_feed_urls()
    now = datetime.now(UTC)

    job = Job(
        status="running",
        total=len(urls),
        started_at=now,
    )
    db.add(job)
    await db.flush()

    tasks = [
        Task(job_id=job.id, url=url, status="pending")
        for url in urls
    ]
    db.add_all(tasks)
    await db.commit()

    await asyncio.gather(
        *[
            arq_pool.enqueue_job("process_task", str(task.id))
            for task in tasks
        ]
    )

    get_logger(job_id=str(job.id)).info(
        "job_created",
        total=len(urls),
        tasks_enqueued=len(tasks),
    )

    return JobCreatedResponse(job_id=job.id)


@router.get("", response_model=JobListResponse)
async def list_jobs(db: AsyncSession = Depends(get_db)) -> JobListResponse:
    result = await db.execute(
        select(Job).order_by(Job.created_at.desc()).limit(JOBS_LIST_LIMIT)
    )
    jobs = result.scalars().all()
    return JobListResponse(
        jobs=[
            JobSummary(
                id=job.id,
                status=job.status,
                total=job.total,
                completed=job.completed,
                failed=job.failed,
                created_at=job.created_at,
                started_at=job.started_at,
                finished_at=job.finished_at,
                elapsed_seconds=elapsed_seconds(job.started_at, job.finished_at),
            )
            for job in jobs
        ]
    )


@router.get("/{job_id}", response_model=JobDetailResponse)
async def get_job(
    job_id: uuid.UUID,
    db: AsyncSession = Depends(get_db),
) -> JobDetailResponse:
    job = await get_job_or_none(db, job_id)
    if job is None:
        raise HTTPException(status_code=404, detail="Job not found")

    if job.finished_at is None:
        await finalize_job_if_done(db, job_id)
        await db.commit()
        await db.refresh(job)

    counts = await task_status_counts(db, job_id)
    return JobDetailResponse(
        id=job.id,
        status=job.status,
        total=job.total,
        completed=counts.get("completed", 0),
        failed=counts.get("failed", 0),
        in_progress=counts.get("in_progress", 0),
        pending=counts.get("pending", 0),
        created_at=job.created_at,
        started_at=job.started_at,
        finished_at=job.finished_at,
        elapsed_seconds=elapsed_seconds(job.started_at, job.finished_at),
    )


@router.get("/{job_id}/events")
async def stream_job_events(
    request: Request,
    job_id: uuid.UUID,
    db: AsyncSession = Depends(get_db),
) -> EventSourceResponse:
    job = await get_job_or_none(db, job_id)
    if job is None:
        raise HTTPException(status_code=404, detail="Job not found")

    return EventSourceResponse(
        job_event_stream(request, job_id, job, db),
        ping=15,
    )


@router.get("/{job_id}/tasks", response_model=TaskListResponse)
async def list_tasks(
    job_id: uuid.UUID,
    status: TaskStatusFilter | None = None,
    db: AsyncSession = Depends(get_db),
) -> TaskListResponse:
    job = await get_job_or_none(db, job_id)
    if job is None:
        raise HTTPException(status_code=404, detail="Job not found")

    base = select(Task).where(Task.job_id == job_id)
    if status is not None:
        base = base.where(Task.status == status.value)

    count_stmt = select(func.count()).where(Task.job_id == job_id)
    if status is not None:
        count_stmt = count_stmt.where(Task.status == status.value)
    total = (await db.execute(count_stmt)).scalar_one()

    result = await db.execute(base.order_by(Task.created_at))
    tasks = result.scalars().all()

    return TaskListResponse(
        tasks=[
            TaskSummary(
                id=t.id,
                url=t.url,
                status=t.status,
                attempts=t.attempts,
                last_error=t.last_error,
                error_kind=t.error_kind,
                time_taken_ms=t.time_taken_ms,
                records_count=t.records_count,
            )
            for t in tasks
        ],
        total=total,
    )


@router.get("/{job_id}/tasks/{task_id}", response_model=TaskDetailResponse)
async def get_task(
    job_id: uuid.UUID,
    task_id: uuid.UUID,
    db: AsyncSession = Depends(get_db),
) -> TaskDetailResponse:
    task = await get_task_for_job_or_none(db, job_id, task_id)
    if task is None:
        raise HTTPException(status_code=404, detail="Task not found")

    return TaskDetailResponse(
        id=task.id,
        job_id=task.job_id,
        url=task.url,
        status=task.status,
        attempts=task.attempts,
        last_error=task.last_error,
        error_kind=task.error_kind,
        time_taken_ms=task.time_taken_ms,
        records_count=task.records_count,
        created_at=task.created_at,
        updated_at=task.updated_at,
    )


@router.get("/{job_id}/tasks/{task_id}/records", response_model=RecordListResponse)
async def list_records(
    job_id: uuid.UUID,
    task_id: uuid.UUID,
    page: int = Query(1, ge=1),
    size: int = Query(20, ge=1, le=100),
    db: AsyncSession = Depends(get_db),
) -> RecordListResponse:
    task = await get_task_for_job_or_none(db, job_id, task_id)
    if task is None:
        raise HTTPException(status_code=404, detail="Task not found")

    total_result = await db.execute(
        select(func.count()).select_from(Record).where(Record.task_id == task_id)
    )
    total = total_result.scalar_one()

    offset = (page - 1) * size
    result = await db.execute(
        select(Record)
        .where(Record.task_id == task_id)
        .order_by(Record.created_at)
        .offset(offset)
        .limit(size)
    )
    records = result.scalars().all()

    return RecordListResponse(
        records=[
            RecordResponse(
                id=r.id,
                title=r.title,
                link=r.link,
                published=r.published,
                author=r.author,
                summary=r.summary,
                created_at=r.created_at,
            )
            for r in records
        ],
        total=total,
        page=page,
        size=size,
    )
