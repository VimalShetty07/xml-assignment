# XML feed ingestion

Fetches 100 RSS/Atom URLs in parallel (backend worker), saves parsed items to PostgreSQL, and shows job progress in a small React dashboard. The UI only talks to the API — it does not fetch or parse feeds.

## Run

Needs **Docker** and **Docker Compose**.

```bash
git clone https://github.com/VimalShetty07/xml-assignment.git
cd xml-assignment
docker compose up --build
```

| What | URL |
|------|-----|
| Dashboard | http://localhost:5173 |
| API docs | http://localhost:8000/docs |

Postgres on the host is port **5433** (not 5432), in case you already run Postgres locally.

No `.env` file is needed for Docker — settings are in `docker-compose.yml`. For a local run without Docker, copy `backend/.env.example` to `backend/.env` (and use `frontend/.env.example` if you run the UI with `npm run dev`).

## Try it

1. Open http://localhost:5173  
2. Click **Start job**  
3. Watch progress on the job page; open a task row to see records or errors  

Feed URLs are in `backend/app/data/feed_data.txt`.
