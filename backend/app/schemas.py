import uuid
from datetime import datetime
from enum import Enum

from pydantic import BaseModel


class JobCreatedResponse(BaseModel):
    job_id: uuid.UUID


class TaskStatusFilter(str, Enum):
    pending = "pending"
    in_progress = "in_progress"
    completed = "completed"
    failed = "failed"


class JobSummary(BaseModel):
    id: uuid.UUID
    status: str
    total: int
    completed: int
    failed: int
    created_at: datetime
    started_at: datetime | None
    finished_at: datetime | None
    elapsed_seconds: float | None


class JobListResponse(BaseModel):
    jobs: list[JobSummary]


class JobDetailResponse(BaseModel):
    id: uuid.UUID
    status: str
    total: int
    completed: int
    failed: int
    in_progress: int
    pending: int
    created_at: datetime
    started_at: datetime | None
    finished_at: datetime | None
    elapsed_seconds: float | None


class TaskSummary(BaseModel):
    id: uuid.UUID
    url: str
    status: str
    attempts: int
    last_error: str | None
    error_kind: str | None
    time_taken_ms: int | None
    records_count: int


class TaskListResponse(BaseModel):
    tasks: list[TaskSummary]
    total: int


class TaskDetailResponse(BaseModel):
    id: uuid.UUID
    job_id: uuid.UUID
    url: str
    status: str
    attempts: int
    last_error: str | None
    error_kind: str | None
    time_taken_ms: int | None
    records_count: int
    created_at: datetime
    updated_at: datetime


class RecordResponse(BaseModel):
    id: uuid.UUID
    title: str | None
    link: str | None
    published: str | None
    author: str | None
    summary: str | None
    created_at: datetime


class RecordListResponse(BaseModel):
    records: list[RecordResponse]
    total: int
    page: int
    size: int
