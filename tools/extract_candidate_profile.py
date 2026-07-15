#!/usr/bin/env python3
"""
Gathers raw candidate data: reads resume.txt and scrapes the portfolio.
Prints combined output for the agent to process and save as candidate_profile.json.
"""

import sys
from pathlib import Path

import requests
from bs4 import BeautifulSoup

DATA_DIR = Path(__file__).parent.parent / ".data"
RESUME_FILE = DATA_DIR / "resume.txt"
PORTFOLIO_URL = "https://jaimenguyen.com/projects"


def scrape_portfolio(url: str) -> str:
    print(f"\n--- PORTFOLIO ({url}) ---", flush=True)
    try:
        resp = requests.get(url, timeout=15, headers={"User-Agent": "Mozilla/5.0"})
        resp.raise_for_status()
        soup = BeautifulSoup(resp.text, "html.parser")
        for tag in soup(["script", "style", "noscript"]):
            tag.decompose()
        return soup.get_text(separator="\n", strip=True)[:6000]
    except Exception as e:
        return f"Portfolio scrape failed: {e}"


def main():
    if not RESUME_FILE.exists():
        print(f"ERROR: Resume not found at {RESUME_FILE}")
        sys.exit(1)

    resume_text = RESUME_FILE.read_text(encoding="utf-8")

    print("--- RESUME ---")
    print(resume_text)

    portfolio_text = scrape_portfolio(PORTFOLIO_URL)
    print(portfolio_text)


if __name__ == "__main__":
    main()
