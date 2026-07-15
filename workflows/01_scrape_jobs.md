# Workflow 01 — Scrape LinkedIn Jobs

## Objective

Scrape fresh LinkedIn job listings for today and save them locally for further processing.

## When to Run

Mon–Thu only. The scraper handles the day check internally and exits cleanly on Fri–Sun.

## Required Inputs

- `APIFY_TOKEN` set in `.env`
- `constants/scraping_config.py` present with `MAX_JOBS`, `DAY_URLS`, `DAY_NAMES`

## Steps

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

## Expected Output

`.data/jobs_YYYY-MM-DD.json` with up to 50 job objects.

Each job contains: `id`, `title`, `companyName`, `location`, `postedAt`, `descriptionText`, `descriptionHtml`, `salary`, `applyUrl`, `link`, `employmentType`, `seniorityLevel`, `applicantsCount`, `companyWebsite`, `companyDescription`, `companyEmployeesCount`, `companyAddress`, and more.

## Edge Cases

- **Fri/Sat/Sun:** Exits cleanly with a skip message. Do not proceed to next workflow.
- **Apify failure:** Script exits with a non-zero code and prints the error. Fix before retrying.

## Files Involved

| File | Purpose |
|------|---------|
| `tools/scrape_linkedin_jobs.py` | Calls Apify, saves raw jobs |
| `constants/scraping_config.py` | MAX_JOBS, DAY_URLS, DAY_NAMES |
| `.data/jobs_YYYY-MM-DD.json` | Raw scraped output |
| `.env` | APIFY_TOKEN |

## Next

Run **Workflow 02 — Deduplicate Jobs**
