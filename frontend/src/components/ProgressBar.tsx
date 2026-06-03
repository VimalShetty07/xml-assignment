import type { JobDetail } from "../api/types";

interface Props {
  job: JobDetail;
}

function Stat({ label, value, color }: { label: string; value: number; color: string }) {
  return (
    <div className="progress-stat">
      <span className="progress-stat-dot" style={{ background: color }} />
      <span className="progress-stat-label">{label}</span>
      <span className="progress-stat-value">{value}</span>
    </div>
  );
}

export function ProgressBar({ job }: Props) {
  const { total, completed, failed, in_progress, pending } = job;
  const pct = (n: number) => (total > 0 ? (n / total) * 100 : 0);

  return (
    <div className="progress-wrap">
      <div
        className="progress-bar"
        role="progressbar"
        aria-valuenow={completed + failed}
        aria-valuemin={0}
        aria-valuemax={total}
      >
        <div
          className="seg completed"
          style={{ width: `${pct(completed)}%` }}
          title={`Completed: ${completed}`}
        />
        <div
          className="seg failed"
          style={{ width: `${pct(failed)}%` }}
          title={`Failed: ${failed}`}
        />
        <div
          className="seg in-progress"
          style={{ width: `${pct(in_progress)}%` }}
          title={`In progress: ${in_progress}`}
        />
        <div
          className="seg pending"
          style={{ width: `${pct(pending)}%` }}
          title={`Pending: ${pending}`}
        />
      </div>

      <div className="progress-stats">
        <Stat label="Completed" value={completed} color="#34a853" />
        <Stat label="Failed" value={failed} color="#ea4335" />
        <Stat label="In progress" value={in_progress} color="#4285f4" />
        <Stat label="Pending" value={pending} color="#5f6368" />
        <Stat label="Total" value={total} color="#9aa0a6" />
      </div>
    </div>
  );
}
