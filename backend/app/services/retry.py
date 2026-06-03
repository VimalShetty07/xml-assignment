import random

from app.config import RETRY_BASE_SECONDS, RETRY_CAP_SECONDS


def compute_backoff_seconds(attempt: int, retry_after: int | None = None) -> float:
    """Exponential backoff with jitter; optional Retry-After from HTTP 429."""
    if retry_after is not None and retry_after > 0:
        return float(retry_after) + random.uniform(0, 1)

    exp = min(RETRY_BASE_SECONDS * (2 ** max(attempt - 1, 0)), RETRY_CAP_SECONDS)
    jitter = random.uniform(0, min(exp, 1.0))
    return exp + jitter
