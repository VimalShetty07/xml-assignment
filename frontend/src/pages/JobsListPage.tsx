import { useMutation, useQuery, useQueryClient } from "@tanstack/react-query";
import { Link, useNavigate } from "react-router-dom";
import { api } from "../api/client";
import { ErrorPanel } from "../components/ErrorPanel";
import { LoadingSkeleton } from "../components/LoadingSkeleton";

function formatElapsed(sec: number | null): string {
  if (sec == null) return "—";
  if (sec < 60) return `${sec.toFixed(1)}s`;
  return `${(sec / 60).toFixed(1)}m`;
}

export function JobsListPage() {
  const navigate = useNavigate();
  const queryClient = useQueryClient();

  const jobsQuery = useQuery({
    queryKey: ["jobs"],
    queryFn: api.listJobs,
    refetchInterval: 5000,
  });

  const createMutation = useMutation({
    mutationFn: api.createJob,
    onSuccess: (data) => {
      queryClient.invalidateQueries({ queryKey: ["jobs"] });
      navigate(`/jobs/${data.job_id}`);
    },
  });

  return (
    <div className="page">
      <header className="page-header">
        <div>
          <h1>Feed jobs</h1>
          <p className="muted">Monitor XML feed parsing runs</p>
        </div>
        <button
          type="button"
          className="btn primary"
          disabled={createMutation.isPending}
          onClick={() => createMutation.mutate()}
        >
          {createMutation.isPending ? "Starting…" : "Start job"}
        </button>
      </header>

      {createMutation.isError && (
        <ErrorPanel
          message={createMutation.error.message}
          onRetry={() => createMutation.mutate()}
        />
      )}

      {jobsQuery.isLoading && <LoadingSkeleton rows={4} />}

      {jobsQuery.isError && (
        <ErrorPanel
          message={jobsQuery.error.message}
          onRetry={() => jobsQuery.refetch()}
        />
      )}

      {jobsQuery.isSuccess && jobsQuery.data.jobs.length === 0 && (
        <div className="panel empty-panel">
          <p>No jobs yet — click <strong>Start job</strong> to process 100 feeds.</p>
        </div>
      )}

      {jobsQuery.isSuccess && jobsQuery.data.jobs.length > 0 && (
        <div className="table-wrap">
          <table>
            <thead>
              <tr>
                <th>Status</th>
                <th>Progress</th>
                <th>Elapsed</th>
                <th>Created</th>
              </tr>
            </thead>
            <tbody>
              {jobsQuery.data.jobs.map((job) => (
                <tr key={job.id}>
                  <td>
                    <Link to={`/jobs/${job.id}`}>
                      <span className={`badge ${job.status}`}>{job.status}</span>
                    </Link>
                  </td>
                  <td>
                    {job.completed} ok · {job.failed} failed / {job.total}
                  </td>
                  <td>{formatElapsed(job.elapsed_seconds)}</td>
                  <td>{new Date(job.created_at).toLocaleString()}</td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>
      )}
    </div>
  );
}
