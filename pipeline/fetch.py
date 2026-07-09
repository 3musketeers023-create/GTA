"""
fetch.py — Pull GTA 6 items from every free source.
No API keys required for any source in this file.

Sources:
  - Google News RSS (aggregates hundreds of outlets -> "everywhere and anywhere")
  - Direct outlet RSS feeds (IGN, GameSpot, PC Gamer, Eurogamer, VGC, Rockstar Newswire)
  - Reddit public JSON (r/GTA6, r/GTAVI, r/rockstargames) — no auth needed for read
  - YouTube channel RSS (Rockstar Games) — no API key needed

Output: list of raw items -> raw_items.json
"""
import json
import re
import time
import hashlib
from pathlib import Path

import feedparser
import requests

HEADERS = {"User-Agent": "gta6-news-engine/1.0 (news aggregation pipeline)"}

KEYWORDS = re.compile(r"gta\s*(vi|6)|grand theft auto\s*(vi|6)", re.IGNORECASE)

RSS_FEEDS = [
    # Google News: this alone covers hundreds of outlets
    "https://news.google.com/rss/search?q=%22GTA+6%22+OR+%22GTA+VI%22+OR+%22Grand+Theft+Auto+VI%22&hl=en-US&gl=US&ceid=US:en",
    # Direct outlet feeds (filtered by keyword below)
    "https://feeds.ign.com/ign/games-all",
    "https://www.gamespot.com/feeds/game-news/",
    "https://www.pcgamer.com/rss/",
    "https://www.eurogamer.net/feed/news",
    "https://www.videogameschronicle.com/feed/",
    "https://www.rockstargames.com/newswire/feed",
    # Rockstar Games YouTube channel (channel_id = UCVg9nCmmfIyP4QcGOnZZ9Qg)
    "https://www.youtube.com/feeds/videos.xml?channel_id=UCVg9nCmmfIyP4QcGOnZZ9Qg",
]

REDDIT_SUBS = ["GTA6", "GTAVI", "rockstargames"]


def item_id(title: str, link: str) -> str:
    return hashlib.sha1(f"{title}|{link}".encode()).hexdigest()[:16]


def is_relevant(text: str, source: str) -> bool:
    # Google News query + GTA subreddits are pre-filtered; others need keyword match
    if "news.google" in source or "reddit:GTA" in source or "reddit:GTAVI" in source:
        return True
    return bool(KEYWORDS.search(text))


def fetch_rss() -> list[dict]:
    items = []
    for url in RSS_FEEDS:
        try:
            feed = feedparser.parse(url, request_headers=HEADERS)
            for e in feed.entries[:30]:
                title = e.get("title", "").strip()
                link = e.get("link", "")
                summary = re.sub(r"<[^>]+>", " ", e.get("summary", ""))[:1000]
                if not title or not link:
                    continue
                if not is_relevant(f"{title} {summary}", url):
                    continue
                items.append({
                    "id": item_id(title, link),
                    "title": title,
                    "link": link,
                    "summary": summary.strip(),
                    "source": feed.feed.get("title", url),
                    "published": e.get("published", ""),
                    "kind": "video" if "youtube" in url else "article",
                })
            print(f"[rss] {url[:60]}... -> {len(feed.entries)} entries")
        except Exception as ex:
            print(f"[rss] FAILED {url}: {ex}")
        time.sleep(1)
    return items


def fetch_reddit() -> list[dict]:
    items = []
    for sub in REDDIT_SUBS:
        for sort in ("hot", "new"):
            url = f"https://www.reddit.com/r/{sub}/{sort}.json?limit=20"
            try:
                r = requests.get(url, headers=HEADERS, timeout=15)
                r.raise_for_status()
                for post in r.json()["data"]["children"]:
                    d = post["data"]
                    if d.get("stickied") or d.get("score", 0) < 50:
                        continue  # only posts with traction
                    title = d["title"].strip()
                    link = f"https://www.reddit.com{d['permalink']}"
                    if not is_relevant(title, f"reddit:{sub}"):
                        continue
                    items.append({
                        "id": item_id(title, link),
                        "title": title,
                        "link": link,
                        "summary": (d.get("selftext") or "")[:1000],
                        "source": f"r/{sub}",
                        "published": time.strftime(
                            "%a, %d %b %Y %H:%M:%S GMT", time.gmtime(d["created_utc"])
                        ),
                        "kind": "community",
                        "score": d.get("score", 0),
                    })
                print(f"[reddit] r/{sub}/{sort} ok")
            except Exception as ex:
                print(f"[reddit] FAILED r/{sub}/{sort}: {ex}")
            time.sleep(2)  # be polite, avoid 429
    return items


def main():
    items = fetch_rss() + fetch_reddit()
    # de-dupe by id within this run
    seen, unique = set(), []
    for it in items:
        if it["id"] not in seen:
            seen.add(it["id"])
            unique.append(it)
    out = Path(__file__).parent / "raw_items.json"
    out.write_text(json.dumps(unique, indent=2, ensure_ascii=False))
    print(f"[fetch] {len(unique)} unique items -> {out}")


if __name__ == "__main__":
    main()
