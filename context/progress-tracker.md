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
- Saves full job JSON to `.tmp/jobs_YYYY-MM-DD.json`
- Requires `APIFY_TOKEN` in `.env`

## In Progress

- None yet.

## Next Up

- TBD

## Open Questions

- What happens if a `.tmp/jobs_YYYY-MM-DD.json` already exists for today — overwrite or skip?
- Should the scraper notify on failure (e.g. Telegram via LinkIt)?

## Architecture Decisions

- **Async polling over sync endpoint**: Apify's `run-sync-get-dataset-items` returned 404 for this actor; switched to async run + poll on `/actor-runs/{id}` + fetch from dataset. More robust for long-running scrapes.
- **Day-based URL mapping**: Each weekday targets a different keyword to broaden coverage across the week without hitting the same search repeatedly.
- **`.tmp/` for intermediates**: Raw scraped JSON is disposable and regeneratable — stored locally, not pushed to cloud until a later processing step decides what's worth keeping.

## Session Notes

- `.venv/` created at project root — use `.venv/bin/python` to run scripts
- Apify token is in `.env` as `APIFY_TOKEN`
- Test run on 2026-07-15 (Wednesday) scraped 25 jobs successfully; MAX_JOBS set to 50 for production runs
