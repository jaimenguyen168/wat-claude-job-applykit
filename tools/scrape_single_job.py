#!/usr/bin/env python3
"""
Scrapes a single job URL. Routes to the appropriate scraper based on the domain.
Usage: .venv/bin/python tools/scrape_single_job.py <job_url>

Supported sources:
  - linkedin.com  → Apify actor ayk_6789/linkedin-job-details-scraper
  (add more handlers below as needed)
"""

import json
import os
import sys
import time
from datetime import datetime, timezone
from pathlib import Path
from urllib.parse import urlparse

import requests
from dotenv import load_dotenv

load_dotenv()

APIFY_TOKEN = os.getenv("APIFY_TOKEN")


# ---------------------------------------------------------------------------
# Source handlers — each returns a dict (schema is source-specific)
# ---------------------------------------------------------------------------

def scrape_linkedin(job_url: str) -> dict:
    """Uses ayk_6789/linkedin-job-details-scraper via Apify REST API."""
    actor_id = "ayk_6789~linkedin-job-details-scraper"
    headers = {"Content-Type": "application/json"}
    params = {"token": APIFY_TOKEN}

    print(f"Starting Apify actor '{actor_id}'...")
    run_resp = requests.post(
        f"https://api.apify.com/v2/acts/{actor_id}/runs",
        json={"startUrls": [{"url": job_url}]},
        headers=headers,
        params=params,
        timeout=30,
    )
    if run_resp.status_code != 201:
        print(f"ERROR: Failed to start actor — {run_resp.status_code}")
        print(run_resp.text)
        sys.exit(1)

    run_data = run_resp.json()["data"]
    run_id = run_data["id"]
    dataset_id = run_data["defaultDatasetId"]
    print(f"Run started: {run_id}")

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
        time.sleep(5)

    if status != "SUCCEEDED":
        print(f"ERROR: Actor run ended with status '{status}'")
        sys.exit(1)

    items_resp = requests.get(
        f"https://api.apify.com/v2/datasets/{dataset_id}/items",
        params={**params, "limit": 1},
        timeout=30,
    )
    items = items_resp.json()
    if not items:
        print("ERROR: No data returned from actor.")
        sys.exit(1)

    return items[0]


# ---------------------------------------------------------------------------
# Router
# ---------------------------------------------------------------------------

HANDLERS = {
    "linkedin.com": scrape_linkedin,
    "www.linkedin.com": scrape_linkedin,
}


def get_handler(url: str):
    domain = urlparse(url).netloc.lower()
    handler = HANDLERS.get(domain)
    if not handler:
        print(f"ERROR: No handler for domain '{domain}'. Add one to HANDLERS in this script.")
        sys.exit(1)
    return handler, domain


# ---------------------------------------------------------------------------
# Entry point
# ---------------------------------------------------------------------------

def main():
    if not APIFY_TOKEN:
        print("ERROR: APIFY_TOKEN not set in .env")
        sys.exit(1)

    if len(sys.argv) < 2:
        print("Usage: .venv/bin/python tools/scrape_single_job.py <job_url>")
        sys.exit(1)

    job_url = sys.argv[1]
    print(f"Scraping: {job_url}")

    handler, domain = get_handler(job_url)
    job = handler(job_url)

    print(f"Retrieved: {job.get('job_title') or job.get('title')} @ {job.get('company_name') or job.get('companyName')}")

    out_dir = Path(__file__).parent.parent / ".data"
    out_dir.mkdir(exist_ok=True)
    out_path = out_dir / "single_job_result.json"

    with open(out_path, "w", encoding="utf-8") as f:
        json.dump(job, f, indent=2, ensure_ascii=False)

    print(f"Saved to {out_path}")


if __name__ == "__main__":
    main()
