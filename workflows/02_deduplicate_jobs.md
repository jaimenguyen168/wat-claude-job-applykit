# Workflow 02 — Deduplicate Jobs

## Objective

Remove any jobs already seen in previous scrape runs, update the seen IDs registry, and produce a clean job list ready for the next stage.

## When to Run

Immediately after Workflow 01 completes successfully.

## Required Inputs

- `.data/jobs_YYYY-MM-DD.json` from today's scrape (Workflow 01)
- `.data/seen_ids.json` (created automatically on first run)

## Steps

Run:
```
.venv/bin/python tools/filter_new_jobs.py
```

**What it does:**
- Reads today's `.data/jobs_YYYY-MM-DD.json`
- Loads `.data/seen_ids.json`
- Filters out any jobs whose `id` already exists in `seen_ids.json`
- Appends new job IDs to `seen_ids.json`
- Overwrites `.data/jobs_YYYY-MM-DD.json` with only the new jobs

## Expected Output

- `.data/jobs_YYYY-MM-DD.json` — deduplicated, contains only unseen jobs
- `.data/seen_ids.json` — updated with today's new IDs

## Edge Cases

- **No jobs file for today:** Exits with an error — run Workflow 01 first.
- **All jobs already seen:** File is overwritten with `[]`. Valid — no new jobs today, stop the pipeline.
- **`seen_ids.json` missing:** Created fresh automatically on first run.

## Files Involved

| File | Purpose |
|------|---------|
| `tools/filter_new_jobs.py` | Deduplicates against seen IDs |
| `.data/jobs_YYYY-MM-DD.json` | Overwritten with new jobs only |
| `.data/seen_ids.json` | Persistent registry of all seen job IDs |

## Next

Run **Workflow 03 — [Next Stage]**
