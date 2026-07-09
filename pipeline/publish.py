"""
publish.py — Move finished articles into the site + update state.

1. Copy articles_out/*.md -> site/content/posts/
2. Append published IDs/titles to data/seen.json (so dedupe works next run)
3. Regenerate sitemap.xml
4. Ping Google with the updated sitemap (free instant-ish indexing nudge)

The GitHub Action commits everything after this; Vercel/Cloudflare Pages
auto-deploys on push. That's the whole "automation" loop.
"""
import json
import os
import re
import shutil
from datetime import datetime, timezone
from pathlib import Path

import requests

ROOT = Path(__file__).parent.parent
POSTS = ROOT / "site" / "content" / "posts"
SEEN_PATH = ROOT / "data" / "seen.json"
SITE_URL = os.environ.get("SITE_URL", "https://example.com").rstrip("/")


def main():
    out_dir = Path(__file__).parent / "articles_out"
    written_path = Path(__file__).parent / "written.json"
    written = json.loads(written_path.read_text()) if written_path.exists() else []

    POSTS.mkdir(parents=True, exist_ok=True)
    for w in written:
        shutil.copy(out_dir / w["file"], POSTS / w["file"])

    # update seen state
    seen = json.loads(SEEN_PATH.read_text()) if SEEN_PATH.exists() else {"ids": [], "titles": []}
    seen["ids"].extend(w["id"] for w in written)
    seen["titles"].extend(w["title"] for w in written)
    seen["ids"] = seen["ids"][-5000:]
    seen["titles"] = seen["titles"][-1000:]
    SEEN_PATH.parent.mkdir(exist_ok=True)
    SEEN_PATH.write_text(json.dumps(seen, indent=2, ensure_ascii=False))

    # sitemap
    urls = [f"{SITE_URL}/"]
    for md in sorted(POSTS.glob("*.md"), reverse=True):
        slug = re.sub(r"^\d{4}-\d{2}-\d{2}-", "", md.stem)
        urls.append(f"{SITE_URL}/post/{md.stem}")
    now = datetime.now(timezone.utc).strftime("%Y-%m-%d")
    entries = "\n".join(
        f"  <url><loc>{u}</loc><lastmod>{now}</lastmod></url>" for u in urls
    )
    sitemap = (
        '<?xml version="1.0" encoding="UTF-8"?>\n'
        '<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">\n'
        f"{entries}\n</urlset>\n"
    )
    (ROOT / "site" / "public" / "sitemap.xml").write_text(sitemap)

    # ping Google (best-effort)
    if written and "example.com" not in SITE_URL:
        try:
            requests.get(
                f"https://www.google.com/ping?sitemap={SITE_URL}/sitemap.xml", timeout=15
            )
            print("[publish] pinged Google sitemap")
        except Exception as ex:
            print(f"[publish] ping failed (non-fatal): {ex}")

    print(f"[publish] {len(written)} articles published, sitemap {len(urls)} urls")


if __name__ == "__main__":
    main()
