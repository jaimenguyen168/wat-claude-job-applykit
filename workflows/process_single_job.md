# Workflow 07 — Process Single Job

## Objective

Process one specific job URL end to end: scrape it, score it against the candidate profile, generate a tailored resume and cover letter, render PDFs, and upload everything to Google Drive and the tracking spreadsheet.

## When to Run

Any time the user passes in a single job URL — LinkedIn or any other supported provider. This is an on-demand workflow, not scheduled.

## Required Inputs

- A job URL (LinkedIn or other supported provider)
- `.data/resume.txt` — candidate resume
- `.data/candidate_profile.json` — structured candidate profile (run Workflow 03 first if missing)
- `application-pack/Resume.dc.html` and `application-pack/Cover Letter.dc.html` — templates
- `credentials.json` + `token.json` — Google OAuth (for the upload step)

---

## Step 1 — Scrape the Job

Detect the provider from the URL domain and run the single-job scraper:

```
.venv/bin/python tools/scrape_single_job.py <job_url>
```

**How routing works:**
- `linkedin.com` → Apify actor `ayk_6789~linkedin-job-details-scraper`
- Other providers → add a handler to `HANDLERS` in `tools/scrape_single_job.py`

**Output:** `.data/single_job_result.json` — raw object in the provider's native schema. Always overwrites the previous result regardless of source.

**Edge cases:**
- Unknown domain → script exits with error listing the unsupported domain. Add a handler before retrying.
- Apify run fails or times out → script exits with the actor status. Check Apify dashboard for details.

---

## Step 2 — Score the Job

Run the single-job scorer to prepare context:

```
.venv/bin/python tools/score_single_job.py
```

This prints the candidate profile, resume, and the full raw job object (whatever schema the provider returned) for you to evaluate.

**Score the job using these rules:**

### Hard Rejections — score 0, verdict: no immediately
- Requires 2+ years of experience
- Tech stack lists only technologies the candidate does not have (C, C++, Ruby, Angular, .NET, Java, Go, Rust) — if that's the entire requirement
- Located in: Florida, Mississippi, Tennessee, Arkansas, Idaho, Oklahoma, Missouri, West Virginia, Indiana — unless explicitly 100% remote

### Base Score — start at 50, adjust up/down

| Signal | Points |
|--------|--------|
| Strong skill overlap (3+ matching skills) | +15 to +20 |
| Moderate skill overlap (1–2 skills) | +5 to +10 |
| No skill overlap | -20 |
| Entry-level / 0–1 year exp | +10 |
| Remote work | +10 |
| Philadelphia, New York, Baltimore, New Jersey | +10 |
| California | +8 |
| Role title matches candidate's focus | +10 |
| High applicant count (500+) | -5 |
| Salary listed and competitive | +5 |

**Verdict threshold: score ≥ 75 → yes, else no**

Once scored, save the verdict:

```
echo '{"score": 82, "verdict": "yes", "reason": "one sentence"}' | .venv/bin/python tools/save_scored_single_job.py
```

**If verdict is no:** stop here. No application pack is generated.

---

## Step 3 — Generate Application Pack

Run the pack preparer to get context:

```
.venv/bin/python tools/prepare_single_job_application_pack.py
```

This prints the resume template, cover letter template, candidate profile, and the full raw job object. It also prints the output directory path.

**If verdict is not yes:** the script exits cleanly with a message — nothing to do.

Using the context printed, generate tailored HTML files and save them to the output directory shown:

**Resume (`resume.html`):**
- Rewrite the intro paragraph to align with the role
- Update TECHNICAL SKILLS to prioritize matching skills (max 9, 3-column grid)
- Pick the 3 most relevant projects; order by relevance to the role
- For web/frontend/full-stack roles: exclude mobile-only projects (React Native, Swift, SwiftUI, Expo)
- Always keep the LANGUAGES section
- If still at risk of 2 pages: drop to 2 projects — do not remove other sections
- No dashes in prose; hyphens only in compound words (e.g. "full-stack")

**Cover Letter (`cover_letter.html`):**
- Fill all `[placeholder]` fields from the job context
- Feature ONE most relevant project
- Update the date to today
- No dashes in prose; hyphens only in compound words

**Also write:**
- `title.txt` — one line, just the job title (used for PDF filename)

---

## Step 4 — Render PDFs

```
.venv/bin/python tools/render_pdf.py single
```

Scans `.data/output/single/` for all HTML files and renders each to PDF. Output filenames follow the pattern `jaime-nguyen-{resume|cover-letter}-{company}-{title}.pdf`.

**Edge cases:**
- Missing `support.js` or `doc-page.js` in output dir → `render_pdf.py` copies them automatically from `application-pack/`
- Blank PDF → custom element failed to load; check that both JS files are present

---

## Step 5 — Upload and Log

```
.venv/bin/python tools/upload_single_job.py
```

This:
1. Reads `single_job_result.json` — exits if verdict is not yes
2. Finds the PDF output dir under `.data/output/single/{job_id}_{company}/`
3. Creates `Jobs/{Company Name}/` in Google Drive if it doesn't exist
4. Uploads resume and cover letter PDFs with public view links
5. Appends a row to the tracking spreadsheet

**Schema note:** `upload_single_job.py` uses `_get()` to read fields across provider schemas — it handles both LinkedIn's field names and any other provider's names as long as the fallback keys are defined in the function.

**Edge cases:**
- No output directory found → run Steps 3 and 4 first
- Missing PDFs → run Step 4 (render) again
- Google auth expired → script triggers OAuth browser flow automatically

---

## Full Command Sequence

```bash
# 1. Scrape
.venv/bin/python tools/scrape_single_job.py <job_url>

# 2. Score
.venv/bin/python tools/score_single_job.py
# → agent scores and outputs verdict JSON
echo '{"score": 82, "verdict": "yes", "reason": "..."}' | .venv/bin/python tools/save_scored_single_job.py

# 3. Generate pack (only if verdict is yes)
.venv/bin/python tools/prepare_single_job_application_pack.py
# → agent writes resume.html, cover_letter.html, title.txt to output dir

# 4. Render
.venv/bin/python tools/render_pdf.py single

# 5. Upload
.venv/bin/python tools/upload_single_job.py
```

---

## Files Involved

| File | Purpose |
|------|---------|
| `tools/scrape_single_job.py` | Routes URL to correct provider, saves raw result |
| `tools/score_single_job.py` | Prints scoring context (raw job + profile) |
| `tools/save_scored_single_job.py` | Merges verdict back into single_job_result.json |
| `tools/prepare_single_job_application_pack.py` | Prints pack context for agent |
| `tools/render_pdf.py single` | Renders HTMLs in output/single/ to PDF |
| `tools/upload_single_job.py` | Uploads PDFs to Drive, logs row to sheet |
| `.data/single_job_result.json` | Single job — always overwritten on new scrape |
| `.data/output/single/{job_id}_{company}/` | HTML and PDF output for this job |

## Adding a New Provider

1. Write a handler function in `tools/scrape_single_job.py`:
   ```python
   def scrape_indeed(job_url: str) -> dict:
       # call Apify actor or scrape directly
       # return raw dict — any schema is fine
   ```
2. Register it: `"indeed.com": scrape_indeed` in `HANDLERS`
3. Add `_get()` fallback keys in `tools/upload_single_job.py`'s `append_row` if the new provider uses different field names
