#!/usr/bin/env python3
"""
Prepares scoring context for a single job from single_job_result.json.
Usage: .venv/bin/python tools/score_single_job.py

Dumps the raw job object as-is so the agent can read any provider's schema.
"""

import json
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent))

from constants.scoring_config import SCORING_PROMPT

DATA_DIR = Path(__file__).parent.parent / ".data"
SINGLE_JOB_FILE = DATA_DIR / "single_job_result.json"
PROFILE_FILE = DATA_DIR / "candidate_profile.json"
RESUME_FILE = DATA_DIR / "resume.txt"


def main():
    if not SINGLE_JOB_FILE.exists():
        print("ERROR: single_job_result.json not found — run scrape_single_job.py first")
        sys.exit(1)

    with open(SINGLE_JOB_FILE, encoding="utf-8") as f:
        job = json.load(f)

    resume = RESUME_FILE.read_text(encoding="utf-8") if RESUME_FILE.exists() else None
    profile = json.load(open(PROFILE_FILE, encoding="utf-8")) if PROFILE_FILE.exists() else None

    if not resume and not profile:
        print("Warning: No resume or profile found — scoring based on job content only.")

    resume_section = f"=== CANDIDATE RESUME ===\n{resume.strip()}\n" if resume else ""

    if profile:
        exp_lines = "\n".join(
            f"  - {e['title']} at {e['company']} ({e['duration']})"
            for e in profile.get("experience", [])
        )
        profile_section = f"""=== CANDIDATE PROFILE (structured) ===
Name: {profile.get('name')}
Skills: {', '.join(profile.get('skills', []))}
Experience:
{exp_lines}
"""
    else:
        profile_section = ""

    print(f"""{resume_section}
{profile_section}
=== JOB TO SCORE ===
{json.dumps(job, indent=2, ensure_ascii=False)}

{SCORING_PROMPT}""")


if __name__ == "__main__":
    main()
