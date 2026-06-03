import { useMemo, useState } from "react";
import { Link, useParams } from "react-router-dom";
import { useQuery } from "@tanstack/react-query";
import { api } from "../api/client";
import type { TaskStatus } from "../api/types";
import { ErrorPanel } from "../components/ErrorPanel";
import { LoadingSkeleton } from "../components/LoadingSkeleton";
import { ProgressBar } from "../components/ProgressBar";
import { TaskTable, type SortDir, type SortKey } from "../components/TaskTable";
import { useJobEvents } from "../hooks/useJobEvents";
import { useLiveElapsed } from "../hooks/useLiveElapsed";
import { filterTasks, isJobRunning } from "../utils/jobProgress";

const FILTERS: { label: string; value: TaskStatus | "" }[] = [
  { label: "All", value: "" },
  { label: "Pending", value: "pending" },
  { label: "In progress", value: "in_progress" },
  { label: "Completed", value: "completed" },
  { label: "Failed", value: "failed" },
];

export function JobDetailPage() {
  const { jobId = "" } = useParams();
  const [statusFilter, setStatusFilter] = useState<TaskStatus | "">("");
  const [sortKey, setSortKey] = useState<SortKey>("status");
  const [sortDir, setSortDir] = useState<SortDir>("asc");

  const jobQuery = useQuery({
    queryKey: ["job", jobId],
    queryFn: () => api.getJob(jobId),
    enabled: Boolean(jobId),
    staleTime: 0,
  });

  const job = jobQuery.data;
  const jobActive = job != null && isJobRunning(job);
  const eventsEnabled = Boolean(jobId) && (job == null || jobActive);

  const tasksQuery = useQuery({
    queryKey: ["tasks", jobId],
    queryFn: () => api.listTasks(jobId),
    enabled: Boolean(jobId),
    staleTime: Infinity,
  });

  useJobEvents(jobId, eventsEnabled);

  const visibleTasks = useMemo(
    () => filterTasks(tasksQuery.data?.tasks ?? [], statusFilter),
    [tasksQuery.data?.tasks, statusFilter],
  );

  const liveElapsed = useLiveElapsed(
    job?.started_at ?? null,
    job?.finished_at ?? null,
    job?.elapsed_seconds ?? null,
    jobActive,
  );

  const onSort = (key: SortKey) => {
    if (sortKey === key) {
      setSortDir((d) => (d === "asc" ? "desc" : "asc"));
    } else {
      setSortKey(key);
      setSortDir("asc");
    }
  };

  return (
    <div className="page">
      <header className="page-header">
        <div>
          <Link to="/" className="back-link">
            ← Jobs
          </Link>
          <h1>Job</h1>
          <p className="mono muted" title={jobId}>
            {jobId.slice(0, 8)}…
          </p>
        </div>
        {job && (
          <span className={`badge ${job.status}`}>{job.status}</span>
        )}
      </header>

      {jobQuery.isLoading && <LoadingSkeleton rows={2} />}

      {jobQuery.isError && (
        <ErrorPanel
          message={jobQuery.error.message}
          onRetry={() => jobQuery.refetch()}
        />
      )}

      {job && (
        <section className="panel">
          <h2>Progress</h2>
          <ProgressBar job={job} />
          {liveElapsed != null && (
            <p className="muted elapsed-line">
              Elapsed:{" "}
              <span className="elapsed-value">{liveElapsed.toFixed(1)}s</span>
            </p>
          )}
        </section>
      )}

      <section className="panel">
        <div className="panel-header">
          <h2>Tasks</h2>
          <div className="filters" role="tablist" aria-label="Filter by status">
            {FILTERS.map((f) => (
              <button
                key={f.label}
                type="button"
                role="tab"
                aria-selected={statusFilter === f.value}
                className={
                  statusFilter === f.value ? "filter active" : "filter"
                }
                onClick={() => setStatusFilter(f.value)}
              >
                {f.label}
              </button>
            ))}
          </div>
        </div>

        {tasksQuery.isLoading && <LoadingSkeleton rows={5} />}

        {tasksQuery.isError && (
          <ErrorPanel
            message={tasksQuery.error.message}
            onRetry={() => tasksQuery.refetch()}
          />
        )}

        {tasksQuery.data && (
          <TaskTable
            jobId={jobId}
            tasks={visibleTasks}
            sortKey={sortKey}
            sortDir={sortDir}
            onSort={onSort}
          />
        )}
      </section>
    </div>
  );
}
