from dataclasses import dataclass, field
import time
import httpx
import feedparser


@dataclass
class ParsedRecord:
    title: str | None
    link: str | None
    published: str | None
    author: str | None
    summary: str | None


@dataclass
class FetchResult:
    ok: bool
    status_code: int | None
    records: list[ParsedRecord] = field(default_factory=list)
    error: str | None = None
    error_kind: str | None = None
    elapsed_ms: int = 0
    bozo: bool = False
    retry_after_seconds: int | None = None


async def fetch_and_parse(url: str, timeout: float = 30.0) -> FetchResult:
    start = time.perf_counter()
    try:
        async with httpx.AsyncClient(timeout=timeout, follow_redirects=True) as client:
            resp = await client.get(url)
    except (httpx.TimeoutException, httpx.TransportError) as e:
        return FetchResult(ok=False, status_code=None, error=str(e),
                           error_kind="transient",
                           elapsed_ms=_ms(start))

    if resp.status_code >= 500:
        return FetchResult(ok=False, status_code=resp.status_code,
                           error=f"server error {resp.status_code}",
                           error_kind="transient", elapsed_ms=_ms(start))
    if resp.status_code == 429:
        return FetchResult(
            ok=False,
            status_code=429,
            error="rate limited (429)",
            error_kind="transient",
            elapsed_ms=_ms(start),
            retry_after_seconds=_parse_retry_after(resp.headers.get("Retry-After")),
        )
    if resp.status_code >= 400:
        return FetchResult(ok=False, status_code=resp.status_code,
                           error=f"client error {resp.status_code}",
                           error_kind="permanent", elapsed_ms=_ms(start))

    parsed = feedparser.parse(resp.content)
    if parsed.bozo and not parsed.entries:
        return FetchResult(ok=False, status_code=resp.status_code,
                           error=f"malformed feed: {parsed.bozo_exception}",
                           error_kind="permanent", bozo=True, elapsed_ms=_ms(start))

    records = [
        ParsedRecord(
            title=e.get("title"),
            link=e.get("link"),
            published=e.get("published", e.get("updated")),
            author=e.get("author"),
            summary=e.get("summary", e.get("description")),
        )
        for e in parsed.entries
    ]
    return FetchResult(ok=True, status_code=resp.status_code, records=records,
                       bozo=bool(parsed.bozo), elapsed_ms=_ms(start))


def _ms(start: float) -> int:
    return int((time.perf_counter() - start) * 1000)


def _parse_retry_after(value: str | None) -> int | None:
    if not value:
        return None
    try:
        return max(int(value), 0)
    except ValueError:
        return None