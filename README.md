# XML feed ingestion

FastAPI backend + Arq worker fetch 100 RSS/Atom URLs, store articles in PostgreSQL, React dashboard for progress and task detail. UI never fetches or parses feeds.

## Run

**Docker + Docker Compose** (recommended):

```bash
git clone https://github.com/VimalShetty07/xml-assignment.git
cd xml-assignment
docker compose up --build
```

| Service | URL |
|---------|-----|
| Frontend | http://localhost:5173 |
| API / OpenAPI | http://localhost:8000/docs |

No `.env` for Docker (see `docker-compose.yml`). Local dev: copy `backend/.env.example` → `backend/.env`; optional `frontend/.env.example` for `npm run dev`.

Postgres on host port **5433** (avoids conflict with local Postgres on 5432).

**Without Docker** (3 terminals): `docker compose up -d postgres redis` → `alembic upgrade head` + `uvicorn app.main:app` + `arq app.worker.WorkerSettings` in `backend/` → `npm run dev` in `frontend/`.

## Backend decisions

- **Concurrency:** I/O-bound fetches; API enqueues and returns `job_id`. **Arq** workers on **Redis** run up to **15** concurrent tasks per worker (`max_jobs=15`).
- **Why queue:** survives API restarts, scales workers horizontally, keeps request handlers light.
- **Retries:** transient errors (timeout, 5xx, 429) → `Retry(defer=…)` with backoff (`app/services/retry.py`), max 4 attempts; 4xx / bad feed → fail once.
- **Parsing:** `feedparser`; `bozo` with no entries = permanent failure.
- **DB:** Postgres, SQLAlchemy async, Alembic. Tables: `jobs` → `tasks` → `records`.


## Frontend decisions

- **Real-time:** **SSE** at `GET /jobs/{id}/events` (one-way progress; simpler than WebSockets for this). Workers publish to Redis; API streams to browser.
- **State:** TanStack Query for API data; `useState` for filters/sort. SSE patches job + task cache.
- **Loading / errors:** per-panel skeletons, error panels with retry, empty state on home.

## Tradeoffs

| Choice | Why / limit |
|--------|-------------|
| Arq vs Celery | Lighter, async-native; less ecosystem |
| SSE per task | Simple; would coalesce events at huge scale |
| Client sort ~100 rows | Fine for assignment; server sort at 1k+ |
| `feed_data.txt` | Static URL list |
| Vite in Docker | Easy local demo; production would use nginx build |

With more time: bulk record inserts, nginx frontend image, idempotency on `POST /jobs`.

## Scale

**10× (~1,000 URLs)**  
- Backend: more worker replicas; SQLAlchemy pool / PgBouncer; bulk inserts; Redis pub/sub volume.  
- Frontend: paginate tasks; throttle SSE to aggregate counts every ~200ms.

**100× (~10,000 URLs)**  
- Backend: `COPY`/partition `records`; queue sharding or Kafka; avoid one hot `jobs` row — derive counts from tasks; stream parses.  
- Frontend: virtualized table, server pagination, aggregated SSE only.

## Layout

```
backend/     API, worker, models, alembic, app/data/feed_data.txt
frontend/    React dashboard
docker-compose.yml
```
