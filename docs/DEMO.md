# Demo checklist

Use this when recording a 2–4 minute walkthrough for reviewers.

## Before recording

```bash
docker compose up --build
```

Wait until all services are healthy (`docker compose ps`).

## Script

1. **Home** — http://localhost:5173  
   - Show empty state or prior jobs  
   - Click **Start job**

2. **Job detail** — auto-navigate after start  
   - Point at progress bar (completed / failed / in progress / pending)  
   - Mention updates are live via SSE (no manual refresh)

3. **Wait** — let a few tasks complete (~10–20 seconds is enough for demo)

4. **Filter** — select **Failed**  
   - Note ~3 feeds often return 403 (bot blocking) in the assignment list

5. **Drill-in** — click a failed task URL  
   - Show `last_error`, `error_kind`, `attempts`, `time_taken_ms`  
   - If records exist, show paginated articles

6. **Optional** — open http://localhost:8000/docs and show `POST /jobs` + SSE endpoint

## Artifacts to add to the repo

- `docs/demo.mp4` — screen recording, or  
- `docs/screenshots/01-home.png` … `05-failed-detail.png`

Link from the main [README](../README.md#demo-flow-2-4-minutes) when files are added.

## QuickTime (macOS)

Cmd+Shift+5 → Record Selected Portion → capture the browser window.
