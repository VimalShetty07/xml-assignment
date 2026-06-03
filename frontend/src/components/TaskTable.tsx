import { Link } from "react-router-dom";
import type { TaskSummary } from "../api/types";

export type SortKey = "status" | "url" | "records_count" | "time_taken_ms";
export type SortDir = "asc" | "desc";

interface Props {
  jobId: string;
  tasks: TaskSummary[];
  sortKey: SortKey;
  sortDir: SortDir;
  onSort: (key: SortKey) => void;
}

function sortTasks(
  tasks: TaskSummary[],
  key: SortKey,
  dir: SortDir,
): TaskSummary[] {
  const mul = dir === "asc" ? 1 : -1;
  return [...tasks].sort((a, b) => {
    const av = a[key] ?? "";
    const bv = b[key] ?? "";
    if (typeof av === "number" && typeof bv === "number") {
      return (av - bv) * mul;
    }
    return String(av).localeCompare(String(bv)) * mul;
  });
}

function SortHeader({
  label,
  column,
  sortKey,
  sortDir,
  onSort,
}: {
  label: string;
  column: SortKey;
  sortKey: SortKey;
  sortDir: SortDir;
  onSort: (k: SortKey) => void;
}) {
  const active = sortKey === column;
  return (
    <th>
      <button type="button" className="sort-btn" onClick={() => onSort(column)}>
        {label}
        {active ? (sortDir === "asc" ? " ↑" : " ↓") : ""}
      </button>
    </th>
  );
}

export function TaskTable({ jobId, tasks, sortKey, sortDir, onSort }: Props) {
  const sorted = sortTasks(tasks, sortKey, sortDir);

  if (sorted.length === 0) {
    return <p className="muted">No tasks match this filter.</p>;
  }

  return (
    <div className="table-wrap">
      <table>
        <thead>
          <tr>
            <SortHeader label="Status" column="status" sortKey={sortKey} sortDir={sortDir} onSort={onSort} />
            <SortHeader label="URL" column="url" sortKey={sortKey} sortDir={sortDir} onSort={onSort} />
            <th>Error</th>
            <SortHeader label="Records" column="records_count" sortKey={sortKey} sortDir={sortDir} onSort={onSort} />
            <SortHeader label="Time (ms)" column="time_taken_ms" sortKey={sortKey} sortDir={sortDir} onSort={onSort} />
            <th>Attempts</th>
          </tr>
        </thead>
        <tbody>
          {sorted.map((t) => (
            <tr key={t.id} className={t.status === "failed" ? "row-failed" : ""}>
              <td>
                <span className={`badge ${t.status}`}>{t.status}</span>
              </td>
              <td className="url-cell">
                <Link to={`/jobs/${jobId}/tasks/${t.id}`}>{t.url}</Link>
              </td>
              <td className="error-cell" title={t.last_error ?? undefined}>
                {t.last_error ? t.last_error.slice(0, 80) : "—"}
              </td>
              <td>{t.records_count}</td>
              <td>{t.time_taken_ms ?? "—"}</td>
              <td>{t.attempts}</td>
            </tr>
          ))}
        </tbody>
      </table>
    </div>
  );
}
