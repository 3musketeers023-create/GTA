"""
dedupe.py — Drop items we've already covered.

Two layers:
  1. Exact ID match against data/seen.json (persisted across runs via git commit)
  2. Fuzzy title similarity — different outlets covering the same story
     ("GTA 6 delayed to Nov 19" vs "Rockstar delays GTA VI to November 19")

Output: new_items.json (only genuinely new stories, best source per story)
"""
import json
import re
from pathlib import Path

ROOT = Path(__file__).parent.parent
SEEN_PATH = ROOT / "data" / "seen.json"
SIMILARITY_THRESHOLD = 0.55  # token-set Jaccard
MAX_ARTICLES_PER_RUN = 1  # keep LLM usage inside free tier

SYNONYMS = {
    "vi": "6", "grand": "", "theft": "", "auto": "gta",
    "november": "nov", "december": "dec", "october": "oct",
    "delays": "delay", "delayed": "delay",
    "reveals": "reveal", "revealed": "reveal", "announces": "announce",
    "announced": "announce", "confirms": "confirm", "confirmed": "confirm",
}
STOPWORDS = {"the", "a", "an", "to", "of", "in", "for", "is", "has", "be",
             "will", "on", "at", "and", "its", "it", "by", "rockstar", "games"}


def tokens(title: str) -> set[str]:
    t = re.sub(r"[^a-z0-9 ]", " ", title.lower())
    out = set()
    for w in t.split():
        w = SYNONYMS.get(w, w)
        if w and w not in STOPWORDS:
            out.add(w)
    return out


def similar(a: str, b: str) -> float:
    ta, tb = tokens(a), tokens(b)
    if not ta or not tb:
        return 0.0
    return len(ta & tb) / len(ta | tb)


def main():
    raw = json.loads((Path(__file__).parent / "raw_items.json").read_text())
    seen = json.loads(SEEN_PATH.read_text()) if SEEN_PATH.exists() else {"ids": [], "titles": []}

    new_items = []
    for it in raw:
        if it["id"] in seen["ids"]:
            continue
        # fuzzy match against recent published titles + this batch
        candidates = seen["titles"][-300:] + [n["title"] for n in new_items]
        if any(similar(it["title"], t) >= SIMILARITY_THRESHOLD for t in candidates):
            continue
        new_items.append(it)

    # prioritize: articles/videos over community posts, then reddit by score
    new_items.sort(key=lambda x: (x["kind"] == "community", -x.get("score", 0)))
    new_items = new_items[:MAX_ARTICLES_PER_RUN]

    out = Path(__file__).parent / "new_items.json"
    out.write_text(json.dumps(new_items, indent=2, ensure_ascii=False))
    print(f"[dedupe] {len(raw)} raw -> {len(new_items)} new")


if __name__ == "__main__":
    main()
