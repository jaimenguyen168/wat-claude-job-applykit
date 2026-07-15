#!/usr/bin/env python3
"""
Filters today's scraped jobs against seen_ids.json.
Removes already-seen jobs, updates seen_ids.json with new ones,
and overwrites today's jobs file with only the new jobs.
"""

import json
import sys
from datetime import datetime, timezone
from pathlib import Path

DATA_DIR = Path(__file__).parent.parent / ".data"
SEEN_IDS_FILE = DATA_DIR / "seen_ids.json"


def load_seen_ids() -> set:
    if not SEEN_IDS_FILE.exists():
        return set()
    with open(SEEN_IDS_FILE, encoding="utf-8") as f:
        return set(json.load(f))


def save_seen_ids(seen_ids: set):
    with open(SEEN_IDS_FILE, "w", encoding="utf-8") as f:
        json.dump(sorted(seen_ids), f, indent=2)


def main():
    today = datetime.now(timezone.utc).strftime("%Y-%m-%d")
    jobs_file = DATA_DIR / f"jobs_{today}.json"

    if not jobs_file.exists():
        print(f"ERROR: No scraped jobs file found for today ({jobs_file})")
        sys.exit(1)

    with open(jobs_file, encoding="utf-8") as f:
        jobs = json.load(f)

    print(f"Loaded {len(jobs)} scraped jobs from {jobs_file.name}")

    seen_ids = load_seen_ids()
    print(f"Loaded {len(seen_ids)} seen IDs")

    new_jobs = [j for j in jobs if str(j["id"]) not in seen_ids]
    duplicate_count = len(jobs) - len(new_jobs)

    print(f"Filtered out {duplicate_count} duplicate(s) — {len(new_jobs)} new job(s) remaining")

    # Update seen_ids with the new job IDs
    new_ids = {str(j["id"]) for j in new_jobs}
    seen_ids.update(new_ids)
    save_seen_ids(seen_ids)
    print(f"saved {len(new_ids)} new ID(s) to {SEEN_IDS_FILE.name} ({len(seen_ids)} total)")

    # Overwrite today's jobs file with only new jobs
    with open(jobs_file, "w", encoding="utf-8") as f:
        json.dump(new_jobs, f, indent=2, ensure_ascii=False)

    print(f"Updated {jobs_file.name} with {len(new_jobs)} new job(s)")


if __name__ == "__main__":
    main()
