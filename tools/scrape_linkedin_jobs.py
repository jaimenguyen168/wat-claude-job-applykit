#!/usr/bin/env python3
"""
Scrapes LinkedIn jobs via Apify (curious_coder/linkedin-jobs-scraper).
Runs Mon–Thu only. Saves 50 results to .tmp/jobs_YYYY-MM-DD.json.
"""

import json
import os
import sys
from datetime import datetime, timezone
from pathlib import Path

import requests
from dotenv import load_dotenv

from constants.scraping_config import DAY_NAMES, DAY_URLS, MAX_JOBS

load_dotenv()

APIFY_TOKEN = os.getenv("APIFY_TOKEN")
ACTOR_ID = "curious_coder~linkedin-jobs-scraper"


def main():
    if not APIFY_TOKEN:
        print("ERROR: APIFY_TOKEN not set in .env")
        sys.exit(1)

    today = datetime.now(timezone.utc)
    weekday = today.weekday()  # 0=Mon, 6=Sun

    if weekday not in DAY_URLS:
        day_name = today.strftime("%A")
        print(f"Skipping — today is {day_name}. Scraper only runs Mon–Thu.")
        sys.exit(0)

    url = DAY_URLS[weekday]
    day_name = DAY_NAMES[weekday]
    print(f"Running scrape for {day_name}: {url}")

    headers = {"Content-Type": "application/json"}
    params = {"token": APIFY_TOKEN}

    # Start actor run
    print(f"Starting Apify actor '{ACTOR_ID}' (max {MAX_JOBS} jobs)...")
    run_resp = requests.post(
        f"https://api.apify.com/v2/acts/{ACTOR_ID}/runs",
        json={"urls": [url], "maxItems": MAX_JOBS},
        headers=headers,
        params=params,
        timeout=30,
    )
    if run_resp.status_code != 201:
        print(f"ERROR: Failed to start actor — {run_resp.status_code}")
        print(run_resp.text)
        sys.exit(1)

    run_id = run_resp.json()["data"]["id"]
    dataset_id = run_resp.json()["data"]["defaultDatasetId"]
    print(f"Run started: {run_id}")

    # Poll until finished
    import time
    while True:
        status_resp = requests.get(
            f"https://api.apify.com/v2/actor-runs/{run_id}",
            params=params,
            timeout=30,
        )
        status = status_resp.json()["data"]["status"]
        print(f"  Status: {status}")
        if status in ("SUCCEEDED", "FAILED", "ABORTED", "TIMED-OUT"):
            break
        time.sleep(10)

    if status != "SUCCEEDED":
        print(f"ERROR: Actor run ended with status '{status}'")
        sys.exit(1)

    # Fetch dataset items
    items_resp = requests.get(
        f"https://api.apify.com/v2/datasets/{dataset_id}/items",
        params={**params, "limit": MAX_JOBS},
        timeout=60,
    )
    jobs = items_resp.json()
    print(f"Retrieved {len(jobs)} jobs.")

    # Save to .tmp/
    out_dir = Path(__file__).parent.parent / ".tmp"
    out_dir.mkdir(exist_ok=True)
    date_str = today.strftime("%Y-%m-%d")
    out_path = out_dir / f"jobs_{date_str}.json"

    with open(out_path, "w", encoding="utf-8") as f:
        json.dump(jobs, f, indent=2, ensure_ascii=False)

    print(f"Saved to {out_path}")


if __name__ == "__main__":
    main()
