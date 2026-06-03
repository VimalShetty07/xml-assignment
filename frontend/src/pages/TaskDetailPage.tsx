import { useState } from "react";
import { Link, useParams } from "react-router-dom";
import { useQuery } from "@tanstack/react-query";
import { api } from "../api/client";
import { ErrorPanel } from "../components/ErrorPanel";
import { LoadingSkeleton } from "../components/LoadingSkeleton";

export function TaskDetailPage() {
  const { jobId = "", taskId = "" } = useParams();
  const [page, setPage] = useState(1);
  const pageSize = 20;

  const taskQuery = useQuery({
    queryKey: ["task", jobId, taskId],
    queryFn: () => api.getTask(jobId, taskId),
    enabled: Boolean(jobId && taskId),
  });

  const recordsQuery = useQuery({
    queryKey: ["records", jobId, taskId, page],
    queryFn: () => api.listRecords(jobId, taskId, page, pageSize),
    enabled:
      Boolean(jobId && taskId) && (taskQuery.data?.records_count ?? 0) > 0,
  });

  const totalPages =
    recordsQuery.data != null
      ? Math.max(1, Math.ceil(recordsQuery.data.total / pageSize))
      : 1;

  return (
    <div className="page">
      <header className="page-header">
        <div>
          <Link to={`/jobs/${jobId}`} className="back-link">
            ← Back to job
          </Link>
          <h1>Task detail</h1>
        </div>
        {taskQuery.data && (
          <span className={`badge ${taskQuery.data.status}`}>
            {taskQuery.data.status}
          </span>
        )}
      </header>

      {taskQuery.isLoading && <LoadingSkeleton rows={3} />}

      {taskQuery.isError && (
        <ErrorPanel
          message={taskQuery.error.message}
          onRetry={() => taskQuery.refetch()}
        />
      )}

      {taskQuery.data && (
        <>
          <section className="panel">
            <h2>Diagnostics</h2>
            <dl className="detail-grid">
              <dt>URL</dt>
              <dd className="mono break">{taskQuery.data.url}</dd>
              <dt>Attempts</dt>
              <dd>{taskQuery.data.attempts}</dd>
              <dt>Error kind</dt>
              <dd>{taskQuery.data.error_kind ?? "—"}</dd>
              <dt>Time taken</dt>
              <dd>
                {taskQuery.data.time_taken_ms != null
                  ? `${taskQuery.data.time_taken_ms} ms`
                  : "—"}
              </dd>
              <dt>Records extracted</dt>
              <dd>{taskQuery.data.records_count}</dd>
              <dt>Last error</dt>
              <dd className="error-full">{taskQuery.data.last_error ?? "—"}</dd>
              <dt>Updated</dt>
              <dd>{new Date(taskQuery.data.updated_at).toLocaleString()}</dd>
            </dl>
          </section>

          {taskQuery.data.records_count > 0 && (
            <section className="panel">
              <h2>Extracted records ({taskQuery.data.records_count})</h2>

              {recordsQuery.isLoading && <LoadingSkeleton rows={4} />}

              {recordsQuery.isError && (
                <ErrorPanel
                  message={recordsQuery.error.message}
                  onRetry={() => recordsQuery.refetch()}
                />
              )}

              {recordsQuery.data && (
                <>
                  <ul className="record-list">
                    {recordsQuery.data.records.map((r) => (
                      <li key={r.id} className="record-card">
                        <h3>{r.title ?? "(no title)"}</h3>
                        {r.link && (
                          <a href={r.link} target="_blank" rel="noreferrer">
                            {r.link}
                          </a>
                        )}
                        <p className="muted">
                          {r.published ?? "—"} · {r.author ?? "unknown author"}
                        </p>
                        {r.summary && (
                          <p className="summary">
                            {r.summary.replace(/<[^>]+>/g, "").slice(0, 400)}
                          </p>
                        )}
                      </li>
                    ))}
                  </ul>
                  {totalPages > 1 && (
                    <div className="pager">
                      <button
                        type="button"
                        className="btn"
                        disabled={page <= 1}
                        onClick={() => setPage((p) => p - 1)}
                      >
                        Previous
                      </button>
                      <span>
                        Page {page} / {totalPages}
                      </span>
                      <button
                        type="button"
                        className="btn"
                        disabled={page >= totalPages}
                        onClick={() => setPage((p) => p + 1)}
                      >
                        Next
                      </button>
                    </div>
                  )}
                </>
              )}
            </section>
          )}
        </>
      )}
    </div>
  );
}
