import { useEffect, useRef } from "react";
import { useQueryClient } from "@tanstack/react-query";
import { eventsUrl } from "../api/client";
import type {
  JobDetail,
  ProgressEvent,
  TaskListResponse,
  TaskStatus,
} from "../api/types";

function applyProgress(data: ProgressEvent) {
  return (prev: JobDetail | undefined): JobDetail | undefined => {
    if (!prev) return prev;

    const terminal =
      data.job_status === "completed" || data.job_status === "failed";

    return {
      ...prev,
      status: data.job_status ?? prev.status,
      completed: data.completed ?? prev.completed,
      failed: data.failed ?? prev.failed,
      total: data.total ?? prev.total,
      in_progress: terminal ? 0 : (data.in_progress ?? prev.in_progress),
      pending: terminal ? 0 : (data.pending ?? prev.pending),
      finished_at: data.finished_at ?? prev.finished_at,
    };
  };
}

function patchTaskList(data: ProgressEvent) {
  return (prev: TaskListResponse | undefined): TaskListResponse | undefined => {
    if (!prev?.tasks?.length || !data.task_id || !data.task_status) {
      return prev;
    }
    const status = data.task_status as TaskStatus;
    return {
      ...prev,
      tasks: prev.tasks.map((t) =>
        t.id === data.task_id
          ? {
              ...t,
              status,
              records_count: data.records_count ?? t.records_count,
            }
          : t,
      ),
    };
  };
}

export function useJobEvents(jobId: string, enabled: boolean) {
  const queryClient = useQueryClient();
  const refreshTimer = useRef<ReturnType<typeof setTimeout> | null>(null);

  useEffect(() => {
    if (!enabled) return;

    const es = new EventSource(eventsUrl(jobId));

    const scheduleSync = (immediate = false) => {
      if (refreshTimer.current) {
        clearTimeout(refreshTimer.current);
        refreshTimer.current = null;
      }
      const delay = immediate ? 0 : 3000;
      refreshTimer.current = setTimeout(() => {
        refreshTimer.current = null;
        queryClient.invalidateQueries({ queryKey: ["tasks", jobId] });
        queryClient.invalidateQueries({ queryKey: ["job", jobId] });
      }, delay);
    };

    const handle = (event: MessageEvent) => {
      try {
        const data = JSON.parse(event.data) as ProgressEvent;
        queryClient.setQueryData<JobDetail>(["job", jobId], applyProgress(data));
        queryClient.setQueryData<TaskListResponse>(
          ["tasks", jobId],
          patchTaskList(data),
        );

        const terminal =
          data.job_status === "completed" || data.job_status === "failed";
        if (terminal) {
          scheduleSync(true);
        } else if (event.type === "progress") {
          scheduleSync(false);
        }
      } catch {
        /* ignore */
      }
    };

    es.addEventListener("snapshot", handle);
    es.addEventListener("progress", handle);

    es.onerror = () => {
      scheduleSync(true);
    };

    return () => {
      es.close();
      if (refreshTimer.current) {
        clearTimeout(refreshTimer.current);
      }
    };
  }, [jobId, enabled, queryClient]);
}
