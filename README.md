# WAT Job Apply Kit

An automated job application pipeline built on the **WAT framework** (Workflows, Agents, Tools). It scrapes LinkedIn job listings daily, scores them against your profile, and generates tailored resume and cover letter PDFs for every role that passes — then uploads everything to Google Drive and logs it in a spreadsheet.

The pipeline runs on a schedule (Mon–Thu at 7am) via Claude Code's scheduled task runner.

---

## How It Works

```
LinkedIn → Scrape → Deduplicate → Score → Generate PDFs → Upload to Drive + Log to Sheets
```

| Step | Workflow | Tool | What it does |
|------|----------|------|--------------|
| 1 | Scrape jobs | `scrape_linkedin_jobs.py` | Pulls up to 50 jobs from LinkedIn via Apify |
| 2 | Deduplicate | `filter_new_jobs.py` | Removes jobs seen in previous runs |
| 3 | Extract profile | `extract_candidate_profile.py` | Reads your resume + portfolio into structured JSON |
| 4 | Score jobs | `score_jobs.py` + `save_scored_jobs.py` | Agent scores each job 0–100 and marks pass/fail |
| 5 | Generate pack | `prepare_application_pack.py` + `render_pdf.py` | Agent writes tailored HTML per job; Playwright renders to PDF |
| 6 | Upload + log | `upload_and_log.py` | Uploads PDFs to Google Drive; appends row to tracking spreadsheet |

Each weekday targets a different LinkedIn search keyword:

| Day | Keyword |
|-----|---------|
| Monday | Front-End Development |
| Tuesday | Mobile Application Development |
| Wednesday | Web Development |
| Thursday | Full-Stack Development |

---

## Project Structure

```
.
├── tools/                        # Python scripts — deterministic execution layer
│   ├── scrape_linkedin_jobs.py   # Workflow 01
│   ├── filter_new_jobs.py        # Workflow 02
│   ├── extract_candidate_profile.py  # Workflow 03
│   ├── score_jobs.py             # Workflow 04 (print context)
│   ├── save_scored_jobs.py       # Workflow 04 (save scores)
│   ├── prepare_application_pack.py   # Workflow 05 (print context)
│   ├── render_pdf.py             # Workflow 05 (render HTML → PDF)
│   └── upload_and_log.py         # Workflow 06
│
├── workflows/                    # Markdown SOPs — agent instructions
│   ├── 01_scrape_jobs.md
│   ├── 02_deduplicate_jobs.md
│   ├── 03_extract_candidate_profile.md
│   ├── 04_score_jobs.md
│   ├── 05_generate_application_pack.md
│   └── 06_upload_and_log.md
│
├── constants/                    # Config files (most are gitignored — personal)
│   ├── scraping_config.py        # MAX_JOBS, day-to-URL mapping (gitignored)
│   ├── profile_config.py         # Portfolio URL (gitignored)
│   ├── scoring_config.py         # Scoring rules and pass threshold (gitignored)
│   ├── application_config.py     # Resume/cover letter generation prompt (gitignored)
│   └── google_config.py          # Drive folder ID + Sheets ID (gitignored)
│
├── application-pack/             # Your resume + cover letter HTML templates (gitignored)
│   ├── Resume.dc.html
│   ├── Cover Letter.dc.html
│   ├── doc-page.js               # Web component for page rendering
│   └── support.js
│
├── context/
│   └── progress-tracker.md       # Implementation log
│
├── .data/                        # Runtime data — gitignored
│   ├── resume.txt                # Plain text resume (required)
│   ├── candidate_profile.json    # Extracted profile (generated)
│   ├── seen_ids.json             # Deduplication registry
│   ├── jobs_YYYY-MM-DD.json      # Today's scraped + scored jobs
│   └── output/YYYY-MM-DD/        # Per-job resume and cover letter PDFs
│
├── .env                          # API keys (gitignored)
├── .env.example                  # Template for required env vars
├── credentials.json              # Google OAuth credentials (gitignored)
├── token.json                    # Google OAuth token (gitignored)
└── requirements.txt              # Python dependencies
```

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

These files are gitignored because they contain personal config. Create each one:

**`constants/scraping_config.py`**
```python
MAX_JOBS = 50

DAY_URLS = {
    0: "https://www.linkedin.com/jobs/search?...",  # Monday search URL
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
```python
SCORING_PROMPT = """..."""   # Your scoring rules and criteria
PASS_THRESHOLD = 75          # Minimum score to generate an application pack
```

**`constants/application_config.py`**
```python
APPLICATION_PROMPT = """..."""  # Instructions for tailoring resume and cover letter
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

The templates use the `doc-page` web component (included in `application-pack/`) to render clean, print-ready pages.

### 6. Install IBM Plex fonts for PDF rendering

The PDF renderer injects local fonts to ensure clean copy-paste text in the output PDFs:

```bash
npm install @ibm/plex
mkdir -p /tmp/ibm-plex-fonts
cp node_modules/@ibm/plex/IBM-Plex-Sans/fonts/split/woff2/IBMPlexSans-Regular.woff2 /tmp/ibm-plex-fonts/ibm-plex-sans-400.woff2
cp node_modules/@ibm/plex/IBM-Plex-Sans/fonts/split/woff2/IBMPlexSans-Medium.woff2  /tmp/ibm-plex-fonts/ibm-plex-sans-500.woff2
cp node_modules/@ibm/plex/IBM-Plex-Sans/fonts/split/woff2/IBMPlexSans-SemiBold.woff2 /tmp/ibm-plex-fonts/ibm-plex-sans-600.woff2
cp node_modules/@ibm/plex/IBM-Plex-Mono/fonts/split/woff2/IBMPlexMono-Regular.woff2 /tmp/ibm-plex-fonts/ibm-plex-mono-400.woff2
cp node_modules/@ibm/plex/IBM-Plex-Mono/fonts/split/woff2/IBMPlexMono-Medium.woff2  /tmp/ibm-plex-fonts/ibm-plex-mono-500.woff2
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

# 4. Print scoring context — then paste output to Claude to score
.venv/bin/python tools/score_jobs.py
# → Claude outputs a JSON array of scores
# → Pipe that output back:
.venv/bin/python tools/save_scored_jobs.py scored.json

# 5. Print application pack context — then paste to Claude to generate HTML
.venv/bin/python tools/prepare_application_pack.py
# → Claude writes resume.html, cover_letter.html, title.txt per job

# 5b. Render HTML files to PDF
.venv/bin/python tools/render_pdf.py

# 6. Upload PDFs to Drive and log to Sheets
.venv/bin/python tools/upload_and_log.py
```

---

## Scheduled Runs

The pipeline runs automatically Mon–Thu at 7am via Claude Code's scheduled task runner. The full workflow (steps 1–6) is orchestrated by Claude Code acting as the agent layer.

To set it up, open Claude Code and run:

```
/schedule
```

Then configure a recurring task with cron `0 7 * * 1-4` pointing at the full pipeline workflow.

---

## Output

For each passing job, the pipeline produces:

```
.data/output/YYYY-MM-DD/
  {job_id}_{Company}/
    resume.html
    jaime-nguyen-resume-{company}-{title}.pdf
    cover_letter.html
    jaime-nguyen-cover-letter-{company}-{title}.pdf
    title.txt
```

PDFs are also uploaded to Google Drive under `Jobs/{Company Name}/` and logged to your tracking spreadsheet with columns for job title, company, score, salary, links, location, and direct links to both PDFs.
