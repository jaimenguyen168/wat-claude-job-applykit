# Workflow 03 — Extract Candidate Profile

## Objective

Gather raw candidate data from the resume and portfolio, then extract a structured profile saved to `.data/candidate_profile.json` for use in job matching and scoring.

## When to Run

Once, or whenever the resume or portfolio changes.

## Required Inputs

- `.data/resume.txt` — plain text resume
- Portfolio live at `https://jaimenguyen.com/projects`

## Steps

### Step 1 — Gather raw data

Run:
```
.venv/bin/python tools/extract_candidate_profile.py
```

**What it does:**
- Reads `.data/resume.txt`
- Launches Playwright headless Chromium and scrapes `https://jaimenguyen.com/projects`
- Prints both resume and portfolio text to stdout

### Step 2 — Extract and save structured profile

The agent reads the printed output and extracts a structured JSON profile with the following fields:

```json
{
  "name", "email", "phone", "location",
  "linkedin", "github", "portfolio",
  "summary",
  "skills": [],
  "education": [{ "school", "degree", "field", "graduated", "gpa" }],
  "experience": [{ "title", "company", "duration", "highlights": [] }],
  "projects": [{ "name", "description", "tech": [] }],
  "achievements": [],
  "languages": []
}
```

Saves the result to `.data/candidate_profile.json`.

## Edge Cases

- **Resume missing:** FATAL — tool exits with code 1 and halts the entire pipeline. Add `.data/resume.txt` before running anything.
- **Portfolio unreachable:** Tool prints a scrape failure warning and continues with resume only.
- **Portfolio not fully rendered:** Tool uses `wait_until=load` + 2s buffer to handle Next.js hydration.

## Output

`.data/candidate_profile.json` — structured candidate profile ready for job matching.

## Files Involved

| File | Purpose |
|------|---------|
| `tools/extract_candidate_profile.py` | Reads resume, scrapes portfolio |
| `.data/resume.txt` | Raw resume input |
| `.data/candidate_profile.json` | Structured profile output |

## Next

Run **Workflow 04 — [Next Stage]**
