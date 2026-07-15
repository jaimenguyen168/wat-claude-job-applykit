#!/usr/bin/env python3
"""
Reads today's passed jobs and the resume/cover letter HTML templates.
Prints per-job context so the agent can generate tailored HTML for each.
The agent writes tailored files to .data/output/{date}/{job_id}/.
"""

import json
import sys
from datetime import datetime, timezone
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent))
from constants.application_config import APPLICATION_PROMPT

DATA_DIR = Path(__file__).parent.parent / ".data"
PACK_DIR = Path(__file__).parent.parent / "application-pack"
RESUME_TEMPLATE = PACK_DIR / "Resume.dc.html"
COVER_LETTER_TEMPLATE = PACK_DIR / "Cover Letter.dc.html"
PROFILE_FILE = DATA_DIR / "candidate_profile.json"


def load_passed_jobs() -> list:
    today = datetime.now(timezone.utc).strftime("%Y-%m-%d")
    jobs_file = DATA_DIR / f"jobs_{today}.json"
    if not jobs_file.exists():
        print(f"ERROR: No jobs file for today ({jobs_file})")
        sys.exit(1)
    with open(jobs_file, encoding="utf-8") as f:
        jobs = json.load(f)
    passed = [j for j in jobs if j.get("verdict") == "yes"]
    if not passed:
        print("No jobs passed the verdict today. Nothing to do.")
        sys.exit(0)
    return passed


def load_profile() -> dict | None:
    if not PROFILE_FILE.exists():
        return None
    with open(PROFILE_FILE, encoding="utf-8") as f:
        return json.load(f)


def output_dir_for(job: dict) -> Path:
    today = datetime.now(timezone.utc).strftime("%Y-%m-%d")
    safe_company = "".join(c if c.isalnum() else "_" for c in job.get("companyName", "unknown"))
    return DATA_DIR / "output" / today / f"{job['id']}_{safe_company}"


def main():
    passed_jobs = load_passed_jobs()
    profile = load_profile()
    resume_template = RESUME_TEMPLATE.read_text(encoding="utf-8")
    cover_letter_template = COVER_LETTER_TEMPLATE.read_text(encoding="utf-8")

    print(f"=== APPLICATION PACK — {len(passed_jobs)} job(s) passed ===\n")

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

    print("=== JOBS TO PROCESS ===")
    for i, job in enumerate(passed_jobs):
        out_dir = output_dir_for(job)
        print(f"""--- JOB {i + 1} of {len(passed_jobs)} ---
ID: {job.get('id')}
Title: {job.get('title')}
Company: {job.get('companyName')}
Location: {job.get('location')}
Score: {job.get('score')} | Reason: {job.get('reason')}
Apply URL: {job.get('applyUrl') or job.get('link')}
Description:
{(job.get('descriptionText') or '')[:2000]}

Output directory: {out_dir}
  → resume.html         (agent writes this)
  → cover_letter.html   (agent writes this)
  → title.txt           (agent writes this — just the job title, one line)
""")

    print("=== AGENT INSTRUCTIONS ===")
    print(APPLICATION_PROMPT)


if __name__ == "__main__":
    main()
