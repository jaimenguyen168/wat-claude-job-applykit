#!/usr/bin/env python3
"""
Receives scored job verdicts from the agent and merges them back into
today's jobs file. Expects a JSON array via stdin or as a file argument.

Usage:
  echo '[{"id": "123", "score": 82, "verdict": "yes", "reason": "..."}]' | .venv/bin/python tools/save_scored_jobs.py
  .venv/bin/python tools/save_scored_jobs.py scores.json
"""

import json
import sys
from datetime import datetime, timezone
from pathlib import Path

DATA_DIR = Path(__file__).parent.parent / ".data"


def main():
    # Accept scores from file arg or stdin
    if len(sys.argv) > 1:
        scores_raw = Path(sys.argv[1]).read_text(encoding="utf-8")
    else:
        scores_raw = sys.stdin.read()

    try:
        scores = json.loads(scores_raw)
    except json.JSONDecodeError as e:
        print(f"ERROR: Invalid JSON input — {e}")
        sys.exit(1)

    scores_by_id = {str(s["id"]): s for s in scores}

    today = datetime.now(timezone.utc).strftime("%Y-%m-%d")
    jobs_file = DATA_DIR / f"jobs_{today}.json"

    if not jobs_file.exists():
        print(f"ERROR: No jobs file for today ({jobs_file})")
        sys.exit(1)

    with open(jobs_file, encoding="utf-8") as f:
        jobs = json.load(f)

    updated = 0
    for job in jobs:
        job_id = str(job.get("id"))
        if job_id in scores_by_id:
            s = scores_by_id[job_id]
            job["score"] = s.get("score")
            job["verdict"] = s.get("verdict")
            job["reason"] = s.get("reason")
            updated += 1

    with open(jobs_file, "w", encoding="utf-8") as f:
        json.dump(jobs, f, indent=2, ensure_ascii=False)

    passed = sum(1 for j in jobs if j.get("verdict") == "yes")
    print(f"Updated {updated} job(s). {passed} passed (verdict: yes).")


if __name__ == "__main__":
    main()
