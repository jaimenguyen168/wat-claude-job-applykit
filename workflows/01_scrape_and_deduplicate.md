# Workflow 01 — Scrape & Deduplicate LinkedIn Jobs

## Objective

Scrape fresh LinkedIn job listings for the day, remove any jobs already seen in previous runs, and produce a clean deduplicated job list ready for the next stage of the pipeline.

## When to Run

Mon–Thu only. The scraper handles the day check internally and exits cleanly on Fri–Sun — no need to guard it externally.

## Required Inputs

- `APIFY_TOKEN` set in `.env`
- `constants/scraping_config.py` present with `MAX_JOBS`, `DAY_URLS`, `DAY_NAMES`

## Steps

### Step 1 — Scrape

Run:
```
.venv/bin/python tools/scrape_linkedin_jobs.py
```

**What it does:**
- Checks today's weekday. If Fri/Sat/Sun, exits immediately.
- Picks the LinkedIn search URL for today's keyword:
  - Mon → Front-End Development
  - Tue → Mobile Application Development
  - Wed → Web Development
  - Thu → Full-Stack Development
- Calls Apify actor `curious_coder~linkedin-jobs-scraper` via REST API
- Polls until the run status is `SUCCEEDED`
- Fetches up to 50 job results from the dataset
- Saves to `.data/jobs_YYYY-MM-DD.json`

**Expected output:** `.data/jobs_YYYY-MM-DD.json` with up to 50 job objects

**Each job object contains:**
`id`, `title`, `companyName`, `location`, `postedAt`, `descriptionText`, `descriptionHtml`, `salary`, `applyUrl`, `link`, `employmentType`, `seniorityLevel`, `applicantsCount`, `companyWebsite`, `companyDescription`, `companyEmployeesCount`, `companyAddress`, and more.

### Step 2 — Deduplicate

Run:
```
.venv/bin/python tools/filter_new_jobs.py
```

**What it does:**
- Reads today's `.data/jobs_YYYY-MM-DD.json`
- Loads `.data/seen_ids.json` (created on first run, grows over time)
- Filters out any jobs whose `id` already exists in `seen_ids.json`
- Appends new job IDs to `seen_ids.json`
- Overwrites `.data/jobs_YYYY-MM-DD.json` with only the new jobs

**Expected output:**
- `.data/jobs_YYYY-MM-DD.json` now contains only unseen jobs
- `.data/seen_ids.json` updated with today's new IDs

## Edge Cases

- **No jobs file for today:** `filter_new_jobs.py` exits with an error — run Step 1 first.
- **All jobs already seen:** File is overwritten with an empty list `[]`. This is valid — it means no new jobs today.
- **`seen_ids.json` missing:** Created fresh on first run of Step 2.
- **Fri/Sat/Sun:** Step 1 exits cleanly with a skip message. Do not run Step 2.

## Output

`.data/jobs_YYYY-MM-DD.json` — deduplicated, ready for the next pipeline stage.

## Files Involved

| File | Purpose |
|------|---------|
| `tools/scrape_linkedin_jobs.py` | Calls Apify, saves raw jobs |
| `tools/filter_new_jobs.py` | Deduplicates against seen IDs |
| `constants/scraping_config.py` | MAX_JOBS, DAY_URLS, DAY_NAMES |
| `.data/jobs_YYYY-MM-DD.json` | Today's job output (intermediate) |
| `.data/seen_ids.json` | Persistent registry of all seen job IDs |
| `.env` | APIFY_TOKEN |
