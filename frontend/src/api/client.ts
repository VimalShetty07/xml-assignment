import type {
  JobDetail,
  JobListResponse,
  RecordListResponse,
  TaskDetail,
  TaskListResponse,
  TaskStatus,
} from "./types";

const API_BASE = import.meta.env.VITE_API_URL ?? "";

async function request<T>(path: string, init?: RequestInit): Promise<T> {
  const res = await fetch(`${API_BASE}${path}`, {
    ...init,
    headers: {
      "Content-Type": "application/json",
      ...init?.headers,
    },
  });
  if (!res.ok) {
    const body = await res.text();
    throw new Error(body || `Request failed (${res.status})`);
  }
  return res.json() as Promise<T>;
}

export const api = {
  listJobs: () => request<JobListResponse>("/jobs"),

  createJob: () =>
    request<{ job_id: string }>("/jobs", { method: "POST" }),

  getJob: (jobId: string) => request<JobDetail>(`/jobs/${jobId}`),

  listTasks: (jobId: string, status?: TaskStatus) => {
    const q = status ? `?status=${status}` : "";
    return request<TaskListResponse>(`/jobs/${jobId}/tasks${q}`);
  },

  getTask: (jobId: string, taskId: string) =>
    request<TaskDetail>(`/jobs/${jobId}/tasks/${taskId}`),

  listRecords: (jobId: string, taskId: string, page = 1, size = 20) =>
    request<RecordListResponse>(
      `/jobs/${jobId}/tasks/${taskId}/records?page=${page}&size=${size}`,
    ),
};

export function eventsUrl(jobId: string): string {
  return `${API_BASE}/jobs/${jobId}/events`;
}
