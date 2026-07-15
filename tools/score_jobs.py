#!/usr/bin/env python3
"""
Prepares job scoring context for the Claude Code agent.
Reads today's jobs + candidate profile and prints each job as a structured
scoring prompt. The agent evaluates each job and saves verdicts back to the file.
"""

import json
import sys
from datetime import datetime, timezone
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent))

from constants.scoring_config import SCORING_PROMPT

DATA_DIR = Path(__file__).parent.parent / ".data"
PROFILE_FILE = DATA_DIR / "candidate_profile.json"
RESUME_FILE = DATA_DIR / "resume.txt"


def load_profile() -> dict | None:
    if not PROFILE_FILE.exists():
        return None
    with open(PROFILE_FILE, encoding="utf-8") as f:
        return json.load(f)


def load_resume() -> str | None:
    if not RESUME_FILE.exists():
        return None
    return RESUME_FILE.read_text(encoding="utf-8")


def load_jobs() -> tuple[Path, list]:
    today = datetime.now(timezone.utc).strftime("%Y-%m-%d")
    jobs_file = DATA_DIR / f"jobs_{today}.json"
    if not jobs_file.exists():
        print(f"ERROR: No jobs file found for today ({jobs_file})")
        sys.exit(1)
    with open(jobs_file, encoding="utf-8") as f:
        return jobs_file, json.load(f)


def format_scoring_context(jobs: list, profile: dict | None, resume: str | None) -> str:
    resume_section = f"=== CANDIDATE RESUME ===\n{resume.strip()}\n" if resume else ""

    if profile:
        exp_lines = "\n".join(f"  - {e['title']} at {e['company']} ({e['duration']})" for e in profile.get("experience", []))
        profile_section = f"""=== CANDIDATE PROFILE (structured) ===
Name: {profile.get('name')}
Skills: {', '.join(profile.get('skills', []))}
Experience:
{exp_lines}
"""
    else:
        profile_section = "" if resume else "=== CANDIDATE PROFILE ===\nNot available — score based on job content only.\n"

    jobs_section = "\n".join(f"""--- JOB {i + 1} of {len(jobs)} ---
ID: {job.get('id')}
Title: {job.get('title')}
Company: {job.get('companyName')}
Location: {job.get('location')}
Employment: {job.get('employmentType')}
Seniority: {job.get('seniorityLevel')}
Salary: {job.get('salary') or 'Not listed'}
Applicants: {job.get('applicantsCount')}
Apply URL: {job.get('applyUrl') or job.get('link')}
Description:
{(job.get('descriptionText') or '')[:1500]}
""" for i, job in enumerate(jobs))

    return f"""{resume_section}
{profile_section}
=== JOBS TO SCORE ===
Total: {len(jobs)} job(s)

{jobs_section}
{SCORING_PROMPT}"""


def main():
    jobs_file, jobs = load_jobs()
    profile = load_profile()
    resume = load_resume()

    if not resume and not profile:
        print("Warning: No resume or profile found — scoring based on job content only.")
    elif not resume:
        print("Warning: resume.txt not found — using structured profile only.")
    elif not profile:
        print("Warning: candidate_profile.json not found — using resume only.")

    unscored = [j for j in jobs if "verdict" not in j]
    if not unscored:
        print("All jobs already scored. Nothing to do.")
        sys.exit(0)

    print(f"Jobs to score: {len(unscored)} of {len(jobs)}")
    print(format_scoring_context(unscored, profile, resume))


if __name__ == "__main__":
    main()
