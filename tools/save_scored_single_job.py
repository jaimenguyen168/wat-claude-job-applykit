#!/usr/bin/env python3
"""
Merges the agent's score/verdict back into single_job_result.json.
Expects a JSON object via stdin or as a file argument.

Usage:
  echo '{"score": 82, "verdict": "yes", "reason": "..."}' | .venv/bin/python tools/save_scored_single_job.py
  .venv/bin/python tools/save_scored_single_job.py result.json
"""

import json
import sys
from pathlib import Path

DATA_DIR = Path(__file__).parent.parent / ".data"
SINGLE_JOB_FILE = DATA_DIR / "single_job_result.json"


def main():
    if len(sys.argv) > 1:
        scores_raw = Path(sys.argv[1]).read_text(encoding="utf-8")
    else:
        scores_raw = sys.stdin.read()

    try:
        verdict = json.loads(scores_raw)
    except json.JSONDecodeError as e:
        print(f"ERROR: Invalid JSON input — {e}")
        sys.exit(1)

    if not SINGLE_JOB_FILE.exists():
        print("ERROR: single_job_result.json not found — run scrape_single_job.py first")
        sys.exit(1)

    with open(SINGLE_JOB_FILE, encoding="utf-8") as f:
        job = json.load(f)

    THRESHOLD = 65
    score = verdict.get("score")
    job["score"] = score
    job["verdict"] = "yes" if isinstance(score, (int, float)) and score >= THRESHOLD else "no"
    job["reason"] = verdict.get("reason")

    with open(SINGLE_JOB_FILE, "w", encoding="utf-8") as f:
        json.dump(job, f, indent=2, ensure_ascii=False)

    print(f"Saved. Score: {job['score']} — Verdict: {job['verdict']}")


if __name__ == "__main__":
    main()
