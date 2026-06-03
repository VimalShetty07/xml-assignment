from pathlib import Path

from app.config import FEED_URL_LIMIT, FEED_URLS_FILE


def load_feed_urls(
    path: Path = FEED_URLS_FILE,
    limit: int = FEED_URL_LIMIT,
) -> list[str]:
    lines = [ln.strip() for ln in path.read_text(encoding="utf-8").splitlines()]
    urls = [ln for ln in lines if ln.startswith("http")]
    if len(urls) < limit:
        raise ValueError(f"expected at least {limit} feed URLs in {path}, found {len(urls)}")
    return urls[:limit]
