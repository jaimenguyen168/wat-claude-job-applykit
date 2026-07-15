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
