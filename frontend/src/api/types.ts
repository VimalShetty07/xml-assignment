export type TaskStatus =
  | "pending"
  | "in_progress"
  | "completed"
  | "failed";

export interface JobSummary {
  id: string;
  status: string;
  total: number;
  completed: number;
  failed: number;
  created_at: string;
  started_at: string | null;
  finished_at: string | null;
  elapsed_seconds: number | null;
}

export interface JobListResponse {
  jobs: JobSummary[];
}

export interface JobDetail {
  id: string;
  status: string;
  total: number;
  completed: number;
  failed: number;
  in_progress: number;
  pending: number;
  created_at: string;
  started_at: string | null;
  finished_at: string | null;
  elapsed_seconds: number | null;
}

export interface TaskSummary {
  id: string;
  url: string;
  status: TaskStatus;
  attempts: number;
  last_error: string | null;
  error_kind: string | null;
  time_taken_ms: number | null;
  records_count: number;
}

export interface TaskListResponse {
  tasks: TaskSummary[];
  total: number;
}

export interface TaskDetail extends TaskSummary {
  job_id: string;
  created_at: string;
  updated_at: string;
}

export interface RecordItem {
  id: string;
  title: string | null;
  link: string | null;
  published: string | null;
  author: string | null;
  summary: string | null;
  created_at: string;
}

export interface RecordListResponse {
  records: RecordItem[];
  total: number;
  page: number;
  size: number;
}

export interface ProgressEvent {
  job_id?: string;
  job_status?: string;
  completed?: number;
  failed?: number;
  total?: number;
  in_progress?: number;
  pending?: number;
  task_id?: string;
  task_status?: string;
  records_count?: number;
  last_error?: string | null;
  error_kind?: string | null;
  finished_at?: string | null;
}
