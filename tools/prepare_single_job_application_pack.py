#!/usr/bin/env python3
"""
Reads single_job_result.json and the resume/cover letter HTML templates.
Prints context so the agent can generate tailored HTML for the single job.
The agent writes tailored files to .data/output/single/{job_id}_{company}/.

Usage: .venv/bin/python tools/prepare_single_job_application_pack.py
"""

import json
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent))
from constants.application_config import APPLICATION_PROMPT

DATA_DIR = Path(__file__).parent.parent / ".data"
PACK_DIR = Path(__file__).parent.parent / "application-pack"
RESUME_TEMPLATE = PACK_DIR / "Resume.dc.html"
COVER_LETTER_TEMPLATE = PACK_DIR / "Cover Letter.dc.html"
PROFILE_FILE = DATA_DIR / "candidate_profile.json"
SINGLE_JOB_FILE = DATA_DIR / "single_job_result.json"


def main():
    if not SINGLE_JOB_FILE.exists():
        print("ERROR: single_job_result.json not found — run scrape_single_job.py first")
        sys.exit(1)

    with open(SINGLE_JOB_FILE, encoding="utf-8") as f:
        job = json.load(f)

    if job.get("verdict") != "yes":
        print(f"Job verdict is '{job.get('verdict')}' — skipping application pack.")
        sys.exit(0)

    profile = json.load(open(PROFILE_FILE, encoding="utf-8")) if PROFILE_FILE.exists() else None
    resume_template = RESUME_TEMPLATE.read_text(encoding="utf-8")
    cover_letter_template = COVER_LETTER_TEMPLATE.read_text(encoding="utf-8")

    # Build output dir from whatever ID/company fields are available
    job_id = job.get("job_posting_id") or job.get("id") or "unknown"
    company_raw = job.get("company_name") or job.get("companyName") or "unknown"
    safe_company = "".join(c if c.isalnum() else "_" for c in company_raw)
    out_dir = DATA_DIR / "output" / "single" / f"{job_id}_{safe_company}"

    print("=== APPLICATION PACK — SINGLE JOB ===\n")

    if profile:
        print("=== CANDIDATE PROFILE ===")
        print(f"Skills: {', '.join(profile.get('skills', []))}")
        print(f"Projects: {', '.join(p['name'] for p in profile.get('projects', []))}")
        print()

    print("=== RESUME TEMPLATE ===")
    print(resume_template)
    print()

    print("=== COVER LETTER TEMPLATE ===")
    print(cover_letter_template)
    print()

    print("=== JOB TO PROCESS ===")
    print(json.dumps(job, indent=2, ensure_ascii=False))
    print()
    print(f"Output directory: {out_dir}")
    print("  → resume.html         (agent writes this)")
    print("  → cover_letter.html   (agent writes this)")
    print("  → title.txt           (agent writes this — just the job title, one line)")
    print()

    print("=== AGENT INSTRUCTIONS ===")
    print(APPLICATION_PROMPT)


if __name__ == "__main__":
    main()
