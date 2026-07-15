# WAT Job Apply Kit

An automated job application pipeline built on the **WAT framework** (Workflows, Agents, Tools). It scrapes LinkedIn job listings daily, scores them against your profile, and generates tailored resume and cover letter PDFs for every role that passes — then uploads everything to Google Drive and logs it in a spreadsheet.

---

## How It Works

```
LinkedIn → Scrape → Deduplicate → Score → Generate PDFs → Upload to Drive + Log to Sheets
```

| Step | Workflow | Tool | What it does |
|------|----------|------|--------------|
| 1 | Scrape jobs | `scrape_linkedin_jobs.py` | Pulls jobs from LinkedIn via Apify |
| 2 | Deduplicate | `filter_new_jobs.py` | Removes jobs seen in previous runs |
| 3 | Extract profile | `extract_candidate_profile.py` | Reads your resume + portfolio into structured JSON |
| 4 | Score jobs | `score_jobs.py` + `save_scored_jobs.py` | Agent scores each job 0–100 and marks pass/fail |
| 5 | Generate pack | `prepare_application_pack.py` + `render_pdf.py` | Agent writes tailored HTML per job; Playwright renders to PDF |
| 6 | Upload + log | `upload_and_log.py` | Uploads PDFs to Google Drive; appends row to tracking spreadsheet |

---

## Setup

### 1. Clone and create a virtual environment

```bash
git clone <repo>
cd wat-job-apply-kit
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
playwright install chromium
```

### 2. Set environment variables

Copy `.env.example` to `.env` and fill in your values:

```bash
cp .env.example .env
```

```env
APIFY_TOKEN=your_apify_token_here
```

Get your Apify token from [apify.com](https://apify.com) — the pipeline uses the `curious_coder/linkedin-jobs-scraper` actor.

### 3. Set up Google OAuth

To enable Drive upload and Sheets logging:

1. Create a project in [Google Cloud Console](https://console.cloud.google.com)
2. Enable the **Google Drive API** and **Google Sheets API**
3. Create OAuth 2.0 credentials (Desktop app) and download as `credentials.json`
4. Place `credentials.json` in the project root
5. Run any tool that calls Google APIs — it will open a browser to authenticate and save `token.json`

### 4. Create your constants files

All constants files are gitignored — they hold your personal config and should be tailored to your situation. Create each one in the `constants/` directory:

**`constants/scraping_config.py`**

Controls how many jobs to fetch and which LinkedIn search URLs to use per day. Adjust the keywords, filters, location, and schedule to match the roles you're targeting. You can use any LinkedIn jobs search URL — generate one by searching with your preferred filters in an incognito window.

```python
MAX_JOBS = 50  # Jobs to fetch per run

DAY_URLS = {
    0: "https://www.linkedin.com/jobs/search?...",  # Monday
    1: "https://www.linkedin.com/jobs/search?...",  # Tuesday
    2: "https://www.linkedin.com/jobs/search?...",  # Wednesday
    3: "https://www.linkedin.com/jobs/search?...",  # Thursday
}

DAY_NAMES = {0: "Monday", 1: "Tuesday", 2: "Wednesday", 3: "Thursday"}
```

**`constants/profile_config.py`**

```python
PORTFOLIO_URL = "https://yourportfolio.com"  # or None to skip
```

**`constants/scoring_config.py`**

Define your own scoring criteria and pass threshold. The agent uses `SCORING_PROMPT` to evaluate each job — include what matters to you: role type, location, seniority, stack, company size, salary, etc. Adjust `PASS_THRESHOLD` to control how selective the filter is.

```python
SCORING_PROMPT = """
Score each job from 0 to 100 based on how well it matches the candidate profile.
Consider: [your criteria here]
"""

PASS_THRESHOLD = 75  # Jobs at or above this score get an application pack
```

**`constants/application_config.py`**

The agent uses `APPLICATION_PROMPT` to tailor the resume and cover letter for each job. Customize it to reflect your preferences — which projects to highlight, how to write the intro, tone, what to avoid, etc.

```python
APPLICATION_PROMPT = """
For each job:
1. RESUME — [your resume tailoring rules]
2. COVER LETTER — [your cover letter rules]
3. Save resume.html, cover_letter.html, title.txt to the output directory shown
4. Run: .venv/bin/python tools/render_pdf.py
"""
```

**`constants/google_config.py`**

```python
DRIVE_FOLDER_ID = "your_drive_folder_id"
SPREADSHEET_ID = "your_spreadsheet_id"
```

### 5. Add your resume and templates

- Place a plain text version of your resume at `.data/resume.txt`
- Add your HTML resume template at `application-pack/Resume.dc.html`
- Add your HTML cover letter template at `application-pack/Cover Letter.dc.html`

The templates use the `doc-page` web component (included in `application-pack/`) to render clean, print-ready pages. You can use any HTML/CSS — the renderer uses Playwright headless Chromium to produce the PDF.

### 6. Install IBM Plex fonts for PDF rendering

The PDF renderer embeds local fonts to ensure clean, selectable text in the output PDFs. If you use a different font, update `_FONT_FILES` in `tools/render_pdf.py` to point at your own woff2 files.

```bash
npm install @ibm/plex
mkdir -p /tmp/ibm-plex-fonts
cp node_modules/@ibm/plex/IBM-Plex-Sans/fonts/split/woff2/IBMPlexSans-Regular.woff2  /tmp/ibm-plex-fonts/ibm-plex-sans-400.woff2
cp node_modules/@ibm/plex/IBM-Plex-Sans/fonts/split/woff2/IBMPlexSans-Medium.woff2   /tmp/ibm-plex-fonts/ibm-plex-sans-500.woff2
cp node_modules/@ibm/plex/IBM-Plex-Sans/fonts/split/woff2/IBMPlexSans-SemiBold.woff2 /tmp/ibm-plex-fonts/ibm-plex-sans-600.woff2
cp node_modules/@ibm/plex/IBM-Plex-Mono/fonts/split/woff2/IBMPlexMono-Regular.woff2  /tmp/ibm-plex-fonts/ibm-plex-mono-400.woff2
cp node_modules/@ibm/plex/IBM-Plex-Mono/fonts/split/woff2/IBMPlexMono-Medium.woff2   /tmp/ibm-plex-fonts/ibm-plex-mono-500.woff2
```

---

## Running Manually

Each workflow can be run independently. Run them in order:

```bash
# 1. Scrape today's jobs
.venv/bin/python tools/scrape_linkedin_jobs.py

# 2. Deduplicate against previously seen jobs
.venv/bin/python tools/filter_new_jobs.py

# 3. Extract candidate profile from resume + portfolio
.venv/bin/python tools/extract_candidate_profile.py

# 4. Print scoring context — paste output to Claude to score
.venv/bin/python tools/score_jobs.py
# Claude outputs a JSON array of scores — save it, then:
.venv/bin/python tools/save_scored_jobs.py scored.json

# 5. Print application pack context — paste to Claude to generate HTML
.venv/bin/python tools/prepare_application_pack.py
# Claude writes resume.html, cover_letter.html, title.txt per job

# 5b. Render HTML to PDF
.venv/bin/python tools/render_pdf.py

# 6. Upload PDFs to Drive and log to Sheets
.venv/bin/python tools/upload_and_log.py
```

---

## Scheduled Runs

The pipeline can run automatically on a schedule using Claude Code's built-in scheduled task runner. The full workflow (steps 1–6) is orchestrated by Claude Code as the agent layer — no separate cron daemon needed.

To set it up, open Claude Code and run `/schedule`, then configure a recurring task with your preferred cron expression and a prompt describing the full pipeline. Adjust the schedule to match the days and times you want to run — for example, weekday mornings before you start your job search.

---

## Output

For each passing job, the pipeline produces:

```
.data/output/YYYY-MM-DD/
  {job_id}_{Company}/
    resume.html
    {name}-resume-{company}-{title}.pdf
    cover_letter.html
    {name}-cover-letter-{company}-{title}.pdf
    title.txt
```

PDFs are also uploaded to Google Drive under `Jobs/{Company Name}/` and logged to your tracking spreadsheet with columns for job title, company, score, salary, location, and direct links to both PDFs.
