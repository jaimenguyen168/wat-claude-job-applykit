# Workflow 06 — Upload PDFs & Log to Spreadsheet

## Objective

For each job that passed scoring today, upload its resume and cover letter PDFs to Google Drive and log a row in the tracking spreadsheet.

## Prerequisites

- Workflow 05 (Generate Application Pack) must be complete
- `credentials.json` must exist at project root (Google OAuth2 client secret)
- `constants/google_config.py` must have `DRIVE_JOBS_FOLDER_ID`, `SPREADSHEET_ID`, `SHEET_NAME`, `SHEET_COLUMNS`

## Required Inputs

- Today's jobs file: `.data/jobs_YYYY-MM-DD.json` (must contain `verdict`, `score`, and all job fields)
- PDF output directory: `.data/output/YYYY-MM-DD/{job_id}_{company}/`
- PDF naming: `jaime-nguyen-resume-*.pdf` and `jaime-nguyen-cover-letter-*.pdf`

## Tool

```
.venv/bin/python tools/upload_and_log.py
```

Optional: pass a date argument to process a specific day.

```
.venv/bin/python tools/upload_and_log.py 2026-07-15
```

## What the Tool Does

1. Loads all jobs with `verdict: "yes"` from today's jobs file
2. Authenticates with Google via OAuth2 (opens browser on first run; reuses `token.json` after)
3. For each passed job:
   - Creates `Jobs/{Company Name}/` subfolder in Google Drive (under `DRIVE_JOBS_FOLDER_ID`) if it doesn't exist
   - Uploads resume PDF and cover letter PDF to that subfolder
   - Sets both files to "anyone with link can view"
   - Appends a row to the spreadsheet with all columns populated

## Spreadsheet Columns (in order)

Link, Score, Title, Company Name, Company URL, Salary, Description (Text), Location, Seniority, Employment Type, Industry, Company Website, Resume, Cover Letter

## Edge Cases

- **No passed jobs**: Tool exits cleanly with a message — nothing to upload
- **Missing PDF dir**: Job is skipped with a warning; others continue
- **Missing resume or cover letter PDF**: Job is skipped with a warning
- **Drive subfolder already exists**: Reused — no duplicate created
- **Token expired**: Refreshed automatically via refresh token

## Output

- PDFs uploaded to Google Drive under `Jobs/{Company Name}/`
- One spreadsheet row per job with all fields + Drive links

## Next

This is the final step in the pipeline. A full run looks like:

1. `tools/scrape_linkedin_jobs.py`
2. `tools/filter_new_jobs.py`
3. `tools/extract_candidate_profile.py` → agent extracts and saves `.data/candidate_profile.json`
4. `tools/score_jobs.py` → agent scores → `tools/save_scored_jobs.py`
5. `tools/prepare_application_pack.py` → agent writes HTML → `tools/render_pdf.py`
6. `tools/upload_and_log.py`
