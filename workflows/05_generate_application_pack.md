# Workflow 05 — Generate Application Pack

## Objective

For each job that passed the verdict, generate a tailored resume and cover letter as PDF files — one page each, text selectable/copiable by LLMs and ATS systems.

## When to Run

After Workflow 04 (score jobs). Only for jobs with `verdict: yes`.

## Required Inputs

- `.data/jobs_YYYY-MM-DD.json` — scored jobs from today
- `application-pack/Resume.dc.html` — resume HTML template
- `application-pack/Cover Letter.dc.html` — cover letter HTML template
- `.data/candidate_profile.json` — optional, used for project/skill selection

## Steps

### Step 1 — Prepare context

Run:
```
.venv/bin/python tools/prepare_application_pack.py
```

Prints:
- Candidate profile summary
- Full resume and cover letter templates
- Each passed job with description, score, and output path
- Agent instructions for tailoring

### Step 2 — Agent generates tailored HTML

For each job, the agent writes two files to `.data/output/{date}/{job_id}_{company}/`:

#### resume.html rules:
- Rewrite the intro paragraph to reflect the role and its specific requirements
- Update TECHNICAL SKILLS to prioritize skills matching the job (max 9, 3-column grid)
- Update PERSONAL PROJECTS to the 3 most relevant (swap in others from profile if needed)
- **Must fit one page** — if too long: remove one project (down to 2) OR remove LANGUAGES section
- Keep all text as real HTML text — no images — so PDF text is fully selectable and copiable

#### cover_letter.html rules:
- Fill all `[placeholder]` fields from the job description
- List ONE most relevant project only (not all of them)
- Update the date to today's date
- Keep all text as real HTML text — copiable by LLMs and ATS

### Step 3 — Render to PDF

Run:
```
.venv/bin/python tools/render_pdf.py
```

Renders all HTML files in today's output directory to PDF via Playwright headless Chromium.
PDFs are saved alongside their HTML source files.

## Output Structure

```
.data/output/{date}/
  {job_id}_{company}/
    resume.html
    resume.pdf
    cover_letter.html
    cover_letter.pdf
```

## Edge Cases

- **No passed jobs:** `prepare_application_pack.py` exits cleanly — nothing to do.
- **Output dir missing:** `render_pdf.py` exits with error — run Step 1 and Step 2 first.
- **Font loading:** Playwright waits 2.5s after load for Google Fonts and web components to render.
- **Two-page resume:** Agent must trim — remove a project or the LANGUAGES section.

## Files Involved

| File | Purpose |
|------|---------|
| `tools/prepare_application_pack.py` | Loads jobs + templates, prints agent context |
| `tools/render_pdf.py` | Renders HTML files to PDF via Playwright |
| `application-pack/Resume.dc.html` | Resume HTML template (gitignored) |
| `application-pack/Cover Letter.dc.html` | Cover letter HTML template (gitignored) |
| `.data/output/{date}/` | Per-job HTML and PDF output |

## Next

Run **Workflow 06 — [Next Stage]**
