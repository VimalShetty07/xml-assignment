import { useEffect, useState } from "react";

/** Tick elapsed time every second while a job is running; freeze when done. */
export function useLiveElapsed(
  startedAt: string | null,
  finishedAt: string | null,
  serverElapsed: number | null,
  isRunning: boolean,
): number | null {
  const [elapsed, setElapsed] = useState<number | null>(serverElapsed);

  useEffect(() => {
    if (!startedAt) {
      setElapsed(serverElapsed);
      return;
    }

    const start = new Date(startedAt).getTime();

    if (finishedAt) {
      const end = new Date(finishedAt).getTime();
      setElapsed((end - start) / 1000);
      return;
    }

    if (!isRunning) {
      setElapsed((prev) => {
        if (prev != null) return prev;
        return serverElapsed;
      });
      return;
    }

    const tick = () => {
      setElapsed((Date.now() - start) / 1000);
    };
    tick();
    const id = setInterval(tick, 1000);
    return () => clearInterval(id);
  }, [isRunning, startedAt, finishedAt, serverElapsed]);

  return elapsed;
}
