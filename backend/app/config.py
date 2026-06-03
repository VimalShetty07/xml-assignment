import os
from pathlib import Path

DATABASE_URL = os.getenv(
    "DATABASE_URL",
    "postgresql+asyncpg://app:app@localhost:5433/feeds",
)
REDIS_URL = os.getenv("REDIS_URL", "redis://localhost:6379/0")

FEED_URLS_FILE = Path(__file__).resolve().parent / "data" / "feed_data.txt"
FEED_URL_LIMIT = 100

# Retry policy (Phase 7)
MAX_TASK_ATTEMPTS = 4
RETRY_BASE_SECONDS = 1.0
RETRY_CAP_SECONDS = 30.0
