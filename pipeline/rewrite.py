"""
rewrite.py — Turn raw news items into ORIGINAL articles.

This step is what makes the site AdSense-eligible and copyright-safe:
we never republish source text. The LLM writes a fresh 300-500 word
article in our own voice, with attribution + link to the original.

Uses Google Gemini free tier (gemini-2.0-flash: 1,500 req/day free).
Set GEMINI_API_KEY as a GitHub Actions secret (free key: aistudio.google.com).

Output: markdown files staged in articles_out/ for publish.py
"""
import json
import os
import re
import time
from datetime import datetime, timezone
from pathlib import Path

import requests

API_KEY = os.environ["GEMINI_API_KEY"]
MODEL = "gemini-2.0-flash"
URL = f"https://generativelanguage.googleapis.com/v1beta/models/{MODEL}:generateContent?key={API_KEY}"

PROMPT = """You are the staff writer for an independent GTA 6 news site.
Write an ORIGINAL news article based on the item below. Rules:
- 300-500 words, your own words entirely. Do NOT copy source phrasing.
- Neutral, factual gaming-journalism tone. No hype-clickbait, no invented facts.
- If the item is a rumor/leak/community post, clearly label it as unconfirmed.
- Add 1-2 sentences of context for readers (release date Nov 19 2026 [correct if item says otherwise], platforms PS5/Xbox Series, Vice City setting).
- End with attribution: "Originally reported by {source}."

Respond ONLY with JSON, no markdown fences:
{{
  "headline": "your own new headline, max 70 chars, title case",
  "slug": "url-safe-slug-max-8-words",
  "excerpt": "one sentence summary, max 160 chars",
  "category": "one of: News, Rumors, Trailers, Community, Release Date",
  "tags": ["3-5 lowercase tags"],
  "body_markdown": "the article in markdown, ## subheadings allowed"
}}

ITEM:
Title: {title}
Source: {source}
Kind: {kind}
Summary: {summary}
Link: {link}
"""


def rewrite(item: dict) -> dict | None:
    prompt = PROMPT.format(**{k: item.get(k, "") for k in ("title", "source", "kind", "summary", "link")})
    body = {
        "contents": [{"parts": [{"text": prompt}]}],
        "generationConfig": {"temperature": 0.7, "maxOutputTokens": 2000},
    }
    for attempt in range(3):
        try:
            r = requests.post(URL, json=body, timeout=60)
            r.raise_for_status()
            text = r.json()["candidates"][0]["content"]["parts"][0]["text"]
            text = re.sub(r"^```(json)?|```$", "", text.strip(), flags=re.MULTILINE).strip()
            return json.loads(text)
        except Exception as ex:
            print(f"[rewrite] attempt {attempt+1} failed: {ex}")
            time.sleep(5 * (attempt + 1))
    return None


def main():
    items = json.loads((Path(__file__).parent / "new_items.json").read_text())
    out_dir = Path(__file__).parent / "articles_out"
    out_dir.mkdir(exist_ok=True)

    written = []
    for item in items:
        art = rewrite(item)
        if not art:
            continue
        now = datetime.now(timezone.utc)
        slug = re.sub(r"[^a-z0-9-]", "", art["slug"].lower().replace(" ", "-"))[:80]
        fname = f"{now.strftime('%Y-%m-%d')}-{slug}.md"
        front = "\n".join([
            "---",
            f'title: "{art["headline"].replace(chr(34), chr(39))}"',
            f"date: {now.isoformat()}",
            f'excerpt: "{art["excerpt"].replace(chr(34), chr(39))}"',
            f"category: {art['category']}",
            f"tags: [{', '.join(art['tags'])}]",
            f"source_url: {item['link']}",
            f'source_name: "{item["source"].replace(chr(34), chr(39))}"',
            "---",
            "",
        ])
        (out_dir / fname).write_text(front + art["body_markdown"])
        written.append({"id": item["id"], "title": item["title"], "file": fname})
        print(f"[rewrite] wrote {fname}")
        time.sleep(4)  # stay under free-tier rate limit (15 RPM)

    (Path(__file__).parent / "written.json").write_text(json.dumps(written, indent=2))
    print(f"[rewrite] {len(written)}/{len(items)} articles written")


if __name__ == "__main__":
    main()
