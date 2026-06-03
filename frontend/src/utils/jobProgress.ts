import type { JobDetail, TaskStatus, TaskSummary } from "../api/types";

const STATUSES: TaskStatus[] = [
  "pending",
  "in_progress",
  "completed",
  "failed",
];

export function countsFromTasks(
  tasks: TaskSummary[],
): Pick<JobDetail, "completed" | "failed" | "in_progress" | "pending"> {
  const counts = { pending: 0, in_progress: 0, completed: 0, failed: 0 };
  for (const t of tasks) {
    counts[t.status] += 1;
  }
  return counts;
}

/** Progress stats from the task table so the bar matches row statuses. */
export function jobProgressFromTasks(
  job: JobDetail,
  tasks: TaskSummary[] | undefined,
): JobDetail {
  if (!tasks?.length) return job;
  return { ...job, ...countsFromTasks(tasks) };
}

/** True while tasks are still pending or in progress (matches the progress bar). */
export function isJobRunning(job: JobDetail): boolean {
  if (job.finished_at) return false;
  if (job.status === "completed" || job.status === "failed") return false;
  const settled = job.completed + job.failed >= job.total;
  const busy = job.in_progress > 0 || job.pending > 0;
  return busy || !settled;
}

export function filterTasks(
  tasks: TaskSummary[],
  status: TaskStatus | "",
): TaskSummary[] {
  if (!status) return tasks;
  return tasks.filter((t) => t.status === status);
}

export { STATUSES };
