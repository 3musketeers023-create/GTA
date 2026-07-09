# GTA 6 News Engine (Vice Wire)

Fully automated GTA 6 news site. Fetches from everywhere → dedupes → LLM
rewrites into original articles → auto-publishes → auto-deploys. Runs on
100% free infrastructure. Total cost: your domain name (~₹800/yr).

## How it works

```
GitHub Actions (cron, every 30 min — free)
  ├─ fetch.py    Google News RSS + IGN/GameSpot/PCG/Eurogamer/VGC/Rockstar
  │              + Reddit (r/GTA6, r/GTAVI, r/rockstargames) + Rockstar YouTube
  ├─ dedupe.py   token-set fuzzy matching + persistent seen.json
  ├─ rewrite.py  Gemini free tier writes ORIGINAL 300-500 word articles
  │              (this is what makes the site AdSense-safe — no scraped content)
  ├─ publish.py  writes markdown → sitemap → pings Google
  └─ git commit  → Vercel/Cloudflare Pages auto-deploys (free)
```

## Setup (30 minutes, one time)

### 1. Repo
- Create a GitHub repo, push this folder to it (branch: `main`)

### 2. Gemini API key (free)
- Go to https://aistudio.google.com → Get API key
- Repo → Settings → Secrets and variables → Actions → New secret:
  - Name: `GEMINI_API_KEY`, value: your key

### 3. Domain + site URL
- Buy a domain (Cloudflare Registrar / Namecheap / Hostinger — cheapest .com you find)
- Repo → Settings → Secrets and variables → Actions → **Variables** tab:
  - Name: `SITE_URL`, value: `https://yourdomain.com`
- Update `site/public/robots.txt` with the same URL
- Rename the site: search for "Vice Wire" in `site/` and change it

### 4. Hosting (pick one, both free)
**Vercel:** vercel.com → Import repo → Root Directory: `site` → Deploy → add custom domain
**Cloudflare Pages:** dash.cloudflare.com → Pages → connect repo →
build command `npm run build`, output `out`, root `site`

### 5. First run
- Repo → Actions → "GTA6 News Pipeline" → Run workflow
- Articles appear in `site/content/posts/`, hosting redeploys automatically
- From now on it runs itself every 30 minutes

### 6. Google Search Console (do this day 1)
- search.google.com/search-console → add your domain → submit sitemap.xml
- This is where your traffic (= money) comes from

### 7. AdSense (apply after ~2-3 weeks of content)
Wait until the site has 25-30+ articles, then apply at adsense.google.com.
After approval:
- Uncomment the AdSense script in `site/app/layout.jsx`, paste your `ca-pub-` ID
- Replace `.ad-slot` placeholder divs with real ad unit code
- Update `site/public/ads.txt` with the line AdSense gives you

## Free-tier budget

| Thing | Limit | Our usage |
|---|---|---|
| GitHub Actions | 2,000 min/mo | ~48 runs/day × ~2 min ≈ 2,880 min ⚠️ |
| Gemini free | 1,500 req/day | max 288/day ✅ |
| Vercel/CF Pages | generous | tiny static site ✅ |

⚠️ If you hit the Actions cap on a private repo, make the repo **public**
(public repos get unlimited Actions minutes) or change cron to `*/45`.

## Tuning

- `MAX_ARTICLES_PER_RUN` in `dedupe.py` — articles per 30-min cycle
- `SIMILARITY_THRESHOLD` — raise if distinct stories get merged, lower if dupes slip through
- Add more RSS feeds to `RSS_FEEDS` in `fetch.py`
- Reddit minimum score (currently 50) in `fetch.py`

## Important legal/policy notes

- Articles are original LLM-written summaries with source attribution — this
  is the aggregation model that survives AdSense review. Never switch to
  copying source text.
- Keep the "not affiliated with Rockstar" disclaimer in the footer.
- Don't use Rockstar's artwork/screenshots without checking their fan-site
  policy (rockstargames.com has fan content guidelines).
- Spot-check articles weekly: LLMs occasionally mangle facts; a wrong release
  date in a headline hurts your credibility and rankings.
