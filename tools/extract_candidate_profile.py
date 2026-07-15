#!/usr/bin/env python3
"""
Gathers raw candidate data: reads resume.txt and scrapes the portfolio.
Prints combined output for the agent to process and save as candidate_profile.json.
"""

import sys
from pathlib import Path

from playwright.sync_api import sync_playwright

from constants.profile_config import PORTFOLIO_URL

DATA_DIR = Path(__file__).parent.parent / ".data"
RESUME_FILE = DATA_DIR / "resume.txt"


def scrape_portfolio(url: str) -> str:
    print(f"\n--- PORTFOLIO ({url}) ---", flush=True)
    try:
        with sync_playwright() as p:
            browser = p.chromium.launch(headless=True)
            page = browser.new_page()
            page.goto(url, wait_until="load", timeout=30000)
            page.wait_for_timeout(2000)
            text = page.inner_text("body")
            browser.close()
        return text[:6000]
    except Exception as e:
        return f"Portfolio scrape failed: {e}"


def main():
    if not RESUME_FILE.exists():
        print(f"FATAL: No resume found at {RESUME_FILE}. Pipeline stopped — all jobs halted.")
        sys.exit(1)

    resume_text = RESUME_FILE.read_text(encoding="utf-8")

    print("--- RESUME ---")
    print(resume_text)

    if PORTFOLIO_URL:
        portfolio_text = scrape_portfolio(PORTFOLIO_URL)
        print(portfolio_text)
    else:
        print("\n--- PORTFOLIO ---\nSkipped (no URL configured)")


if __name__ == "__main__":
    main()
