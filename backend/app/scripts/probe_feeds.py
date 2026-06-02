#!/usr/bin/env python3
"""Probe first N feeds from feeds.txt using fetch_and_parse."""
import asyncio
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2] 
sys.path.insert(0, str(ROOT))

from app.services.xml_feed import fetch_and_parse

FEEDS = ROOT / "app" / "data" / "feed_data.txt"
LIMIT = 100


def load_urls(path: Path, limit: int) -> list[str]:
    lines = [ln.strip() for ln in path.read_text().splitlines() if ln.strip()]
    return lines[:limit]


async def probe_one(url: str) -> dict:
    r = await fetch_and_parse(url)
    return {
        "url": url[:60] + ("…" if len(url) > 60 else ""),
        "ok": r.ok,
        "status": r.status_code,
        "entries": len(r.records),
        "error_kind": r.error_kind or "-",
        "bozo": r.bozo,
        "ms": r.elapsed_ms,
        "error": (r.error or "")[:40],
    }


async def main() -> None:
    urls = load_urls(FEEDS, LIMIT)
    rows = []
    for url in urls:
        rows.append(await probe_one(url))

    cols = ("ok", "status", "entries", "error_kind", "bozo", "ms", "url")
    print(f"{'ok':>4} {'status':>6} {'entries':>7} {'error_kind':>10} {'bozo':>5} {'ms':>6}  url")
    print("-" * 100)
    for row in rows:
        print(
            f"{str(row['ok']):>4} {str(row['status'] or '-'):>6} {row['entries']:>7} "
            f"{row['error_kind']:>10} {str(row['bozo']):>5} {row['ms']:>6}  {row['url']}"
        )

    ok = sum(1 for r in rows if r["ok"])
    perm = sum(1 for r in rows if r["error_kind"] == "permanent")
    trans = sum(1 for r in rows if r["error_kind"] == "transient")
    bozo_ok = sum(1 for r in rows if r["ok"] and r["bozo"])
    print()
    print(f"probed={len(rows)} ok={ok} permanent={perm} transient={trans} bozo-but-ok={bozo_ok}")


if __name__ == "__main__":
    asyncio.run(main())