# Progress Tracker

Update this file after every meaningful implementation change.

## Current Phase

- In Progress

## Current Goal

- Building the WAT job application pipeline — one tool at a time

## Completed

### 00 — LinkedIn Job Scraper (`tools/scrape_linkedin_jobs.py`)

- Calls Apify actor `curious_coder~linkedin-jobs-scraper` via REST API
- Runs Mon–Thu only; each day maps to a different LinkedIn search URL:
  - Mon: Front-End Development
  - Tue: Mobile Application Development
  - Wed: Web Development
  - Thu: Full-Stack Development
- Scrapes 50 jobs per run, polls Apify until status = SUCCEEDED
- Saves full job JSON to `.data/jobs_YYYY-MM-DD.json`
- Requires `APIFY_TOKEN` in `.env`

---

### 01 — Job Deduplicator (`tools/filter_new_jobs.py`)

- Reads today's `.data/jobs_YYYY-MM-DD.json`
- Compares each job `id` against `.data/seen_ids.json` (persistent registry)
- Filters out already-seen jobs, keeps only new ones
- Appends new IDs to `seen_ids.json`
- Overwrites today's jobs file with only the new jobs
- `seen_ids.json` is created automatically on first run

---

### 02 — Candidate Profile Extractor (`tools/extract_candidate_profile.py`)

- Reads `.data/resume.txt` — FATAL exit (halts all jobs) if missing
- Optionally scrapes portfolio using Playwright headless Chromium (Next.js-safe)
- Portfolio URL lives in `constants/profile_config.py` — set to `None` to skip
- Prints combined resume + portfolio text for the agent to extract and save as `.data/candidate_profile.json`
- Profile fields: name, contact, summary, skills, education, experience, projects, achievements, languages

---

### 03 — Job Scorer (`tools/score_jobs.py` + `tools/save_scored_jobs.py`)

- `score_jobs.py` reads today's unscored jobs + resume + structured profile, prints full scoring context for the agent
- Scoring prompt and rules live in `constants/scoring_config.py` (gitignored, personal)
- Agent scores each job 0–100 and outputs a JSON array with `id`, `score`, `verdict`, `reason`
- `save_scored_jobs.py` receives the JSON array (stdin or file) and merges `score`, `verdict`, `reason` back into today's jobs file
- Scoring rules and threshold live in `constants/scoring_config.py` (gitignored, personal)
- First live run: 50 jobs scored, 13 passed

---

### 04 — Application Pack Generator (`tools/prepare_application_pack.py` + `tools/render_pdf.py`)

- `prepare_application_pack.py` reads passed jobs + resume/cover letter HTML templates + profile, prints full context for the agent
- Agent tailors each resume and cover letter per job and saves HTML to `.data/output/{date}/{job_id}_{company}/`
- `render_pdf.py` scans today's output dir and renders all HTML files to PDF via Playwright
- Agent instructions live in `constants/application_config.py` (gitignored, personal)
- `application-pack/` is gitignored — personal templates stay local
- Output: `resume.pdf` and `cover_letter.pdf` per job (HTML files are intermediates)

---

### 05 — Drive Upload & Spreadsheet Logger (`tools/upload_and_log.py`)

- Authenticates via Google OAuth2 using `credentials.json` / `token.json` (Drive + Sheets scopes)
- For each passed job, creates `Jobs/{Company Name}/` subfolder in Google Drive if it doesn't exist
- Uploads resume and cover letter PDFs with public "anyone with link" view permission
- Appends a row to the tracking spreadsheet with all 14 columns: Link, Score, Title, Company Name, Company URL, Salary, Description (Text), Location, Seniority, Employment Type, Industry, Company Website, Resume (link), Cover Letter (link)
- Skips jobs with missing output dirs or PDFs; exits cleanly if no passed jobs
- Drive folder ID and spreadsheet ID live in `constants/google_config.py` (gitignored)

---

### 05.1 — Constants Import Fix (`tools/prepare_application_pack.py` + `tools/upload_and_log.py`)

- Added `sys.path.insert(0, str(Path(__file__).parent.parent))` to both tools before constants imports
- Fixes `ModuleNotFoundError: No module named 'constants'` when tools are run from the project root
- Same fix already present in `tools/score_jobs.py`

---

### 05.2 — Constants Import Fix (`tools/scrape_linkedin_jobs.py` + `tools/extract_candidate_profile.py`)

- Added `sys.path.insert(0, str(Path(__file__).parent.parent))` to both tools before constants imports
- Same fix as 05.1 — needed when the scheduled task runner invokes tools from a different working directory
- All 5 tools that import from `constants/` now have this fix

---

### 05.3 — PDF Rendering Fix (`tools/render_pdf.py`)

- **Root cause of blank PDFs**: HTML uses `doc-page:not(:defined) { visibility: hidden; }` — when `support.js` / `doc-page.js` failed to load, the custom element was never defined, hiding all content
- Fixed by copying `support.js` and `doc-page.js` into each job's output dir before rendering, then using `page.goto(file://...)` with `wait_until="networkidle"` + `wait_for_function("customElements.get('doc-page') !== undefined")` instead of `page.set_content()`
- **Root cause of garbled copy-paste text**: IBM Plex Sans variable font encodes glyphs in a way that breaks PDF text extraction ("and" → "an d")
- Fixed by downloading static per-weight woff2 files from `@ibm/plex` npm package (stored in `/tmp/ibm-plex-fonts/`) and injecting them as base64 `@font-face` rules directly into the HTML before rendering; also added `font-variant-ligatures: none` to prevent glyph ordering issues
- Removes Google Fonts `<link>` tags before rendering so fonts load from embedded data URIs, not the network

---

### 05.4 — Scraper `count` Parameter Fix (`tools/scrape_linkedin_jobs.py`)

- Actor input parameter is `count`, not `maxItems` — the actor silently ignored `maxItems` and scraped ~89 jobs per run instead of 50
- Fixed by changing `"maxItems": MAX_JOBS` → `"count": MAX_JOBS` in the actor run payload

---

### 06 — Landing Page (`web/`)

- Initialized Astro project in `web/` with React + TypeScript + Tailwind CSS v4
- Using pnpm as the package manager; esbuild build approval persisted via `pnpm.json`
- `astro.config.mjs` configured with `site` and `base` for GitHub Pages deployment at `jaimenguyen168.github.io/wat-claude-job-applykit`
- Added `.github/workflows/deploy.yml` — GitHub Actions CI/CD that triggers on push to `main` when `web/**` changes, builds with pnpm, and deploys to GitHub Pages via `actions/deploy-pages`
- GitHub repo Pages source must be set to **GitHub Actions** (not a branch) for the deploy step to work
- Content replaced with real app structure: 9 workflow nodes, 4 setup steps, real tool commands matching the actual codebase
- All components converted from `.astro` to `.tsx` React components following the appshelf pattern
- Structure: `src/features/job-apply-kit/components/` + `views/JobApplyKitView.tsx` mounted via `client:load` in slim `index.astro`
- Components: `JAKHeader`, `JAKHero`, `JAKWorkflowSection`, `JAKSetupSection`, `JAKFooter`, `GearDecor`, `Connector`, `BotEndMarker`
- Theme: CSS vars on `[data-theme]`, `ThemeToggle.tsx` persists to `localStorage` key `jak-theme`
- All component styles consolidated in `global.css`; old `.astro` component files deleted

---

### 07 — Single-Job Scraper (`tools/scrape_single_job.py`)

- Accepts any job URL as a CLI argument; routes to the correct provider based on domain
- `HANDLERS` dict maps domain → handler function — adding a new source is one function + one dict entry
- LinkedIn (`linkedin.com`) → Apify actor `ayk_6789~linkedin-job-details-scraper` (async run + poll)
- Output schema is source-specific — no normalization forced across providers
- Always overwrites `.data/single_job_result.json` — one file, latest job wins regardless of source

---

### 08 — Single-Job Pipeline

**Tools:**

- `tools/scrape_single_job.py` — routes any job URL to the correct provider by domain; LinkedIn uses Apify `ayk_6789~linkedin-job-details-scraper`; always overwrites `.data/single_job_result.json`
- `tools/score_single_job.py` — prints raw job object + candidate profile for agent to score; schema-agnostic
- `tools/save_scored_single_job.py` — merges agent's `{score, verdict, reason}` back into `single_job_result.json`
- `tools/prepare_single_job_application_pack.py` — prints raw job + templates for agent; exits early if verdict is not yes; output goes to `.data/output/single/{job_id}_{company}/`
- `tools/render_pdf.py single` — no changes needed; pass `single` as the dir arg to render `.data/output/single/`
- `tools/upload_single_job.py` — uploads PDFs to Drive, logs to sheet; uses `_get()` to read any provider's field names

**Workflow:** `workflows/process_single_job.md` — full SOP for the on-demand single-job flow

---

### 09 — Landing Page Tab Switcher

- Added two-tab switcher to `JAKWorkflowSection`: **Batch · daily** (9 nodes) and **Single · on-demand** (8 nodes)
- Tab state lifted to `JobApplyKitView` and passed down to `JAKHero`, `JAKWorkflowSection`, and `JAKFooter`
- `JAKHero` terminal command switches with tab: `scrape_linkedin_jobs.py` (batch) → `scrape_single_job.py <url>` (single)
- Handnote updates per tab: "9 nodes, fully linear, zero clicks" ↔ "8 nodes, one URL, done"
- Footer node count updates per tab: "9 nodes" ↔ "8 nodes"
- Single flow nodes: URL Input → Single Job Scraper → Profile Extractor → Single Job Scorer → Score Gate → Single Application Pack Generator → Single PDF Renderer → Single Drive & Sheets
- CSS: `.flow-tabs`, `.flow-tab`, `.flow-tab--active` added to `global.css`

---

## In Progress

- None yet.

## Next Up

- TBD

## Open Questions

- What happens if a `.data/jobs_YYYY-MM-DD.json` already exists for today — overwrite or skip?
- Should the scraper notify on failure (e.g. Telegram via LinkIt)?

## Architecture Decisions

- **Async polling over sync endpoint**: Apify's `run-sync-get-dataset-items` returned 404 for this actor; switched to async run + poll on `/actor-runs/{id}` + fetch from dataset. More robust for long-running scrapes.
- **Day-based URL mapping**: Each weekday targets a different keyword to broaden coverage across the week without hitting the same search repeatedly.
- **`.data/` for intermediates**: Raw scraped JSON is disposable and regeneratable — stored locally, not pushed to cloud until a later processing step decides what's worth keeping.

## Session Notes

- `.venv/` created at project root — use `.venv/bin/python` to run scripts
- Apify token is in `.env` as `APIFY_TOKEN`
- Test run on 2026-07-15 (Wednesday) scraped 25 jobs successfully; MAX_JOBS set to 50 for production runs
