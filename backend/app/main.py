from fastapi import FastAPI, HTTPException
import httpx
import feedparser

FEED_URL = "https://1password.com/blog/index.xml"

app = FastAPI()

@app.get("/test")
def test():
    return {"working"}

@app.get("/test2")
def test2():
    try:
        response = httpx.get(FEED_URL, timeout=30.0, follow_redirects=True)
        response.raise_for_status()
    except httpx.HTTPError as e:
        raise HTTPException(status_code=502, detail=f"Fetch failed: {e}")
    parsed = feedparser.parse(response.content)
    articles = []
    for entry in parsed.entries[:5]:
        articles.append({
            "title": entry.get("title"),
            "link": entry.get("link"),
            "published": entry.get("published", entry.get("updated")),
            "author": entry.get("author"),
            "summary": entry.get("summary", entry.get("description")),
        })
    return {
        "feed_url": FEED_URL,
        "feed_title": parsed.feed.get("title"),
        "total_entries": len(parsed.entries),
        "parse_warning": bool(parsed.bozo),
        "articles": articles,
    }