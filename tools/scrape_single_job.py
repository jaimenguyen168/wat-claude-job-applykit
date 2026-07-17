#!/usr/bin/env python3
"""
Scrapes a single job URL. Routes to the appropriate scraper based on the domain.
Usage: .venv/bin/python tools/scrape_single_job.py <job_url>

Supported sources:
  - linkedin.com      → LinkedIn guest API (free, no browser needed)
  - indeed.com        → Playwright headless Chromium (direct DOM scrape)
  - ziprecruiter.com  → Playwright headless Chromium (direct DOM scrape)
  - jobgether.com         → requests + JSON-LD schema extraction (no browser needed)
  - jobright.ai           → requests + JSON-LD schema extraction (no browser needed)
  - joinhandshake.com     → requests + JSON-LD schema extraction (no browser needed)
  (add more handlers below as needed)
"""

import html
import json
import re
import sys
from pathlib import Path
from urllib.parse import urlparse, urlunparse, parse_qs

import requests
from dotenv import load_dotenv

load_dotenv()


# ---------------------------------------------------------------------------
# Source handlers — each returns a dict (schema is source-specific)
# ---------------------------------------------------------------------------

def scrape_linkedin(job_url: str) -> dict:
    """Scrapes a LinkedIn job via the public guest API — no Apify, no login needed."""
    # Extract numeric job ID from any LinkedIn job URL format
    job_id_match = re.search(r"/(?:jobs/view|jobs/collections|offer)/(?:[^/]+-)?(\d+)", job_url)
    if not job_id_match:
        job_id_match = re.search(r"(\d{7,})", job_url)
    if not job_id_match:
        print("ERROR: Could not extract job ID from LinkedIn URL.")
        sys.exit(1)
    job_id = job_id_match.group(1)
    canonical_url = f"https://www.linkedin.com/jobs/view/{job_id}/"
    print(f"Scraping LinkedIn job {job_id} via guest API...")

    resp = requests.get(
        f"https://www.linkedin.com/jobs-guest/jobs/api/jobPosting/{job_id}",
        headers={"User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36"},
        timeout=30,
    )
    resp.raise_for_status()
    resp.encoding = "utf-8"
    raw = resp.text

    def first(pattern, flags=re.DOTALL):
        m = re.search(pattern, raw, flags)
        return html.unescape(m.group(1).strip()) if m else None

    # Description: strip HTML tags
    desc_raw = first(r'class="show-more-less-html__markup[^"]*">(.*?)</div>')
    description = None
    if desc_raw:
        description = re.sub(r"<[^>]+>", " ", desc_raw)
        description = html.unescape(description)
        description = re.sub(r"\s{2,}", "\n", description).strip()

    # Job criteria: [seniority_level, employment_type, job_function, industries]
    criteria = re.findall(r'class="description__job-criteria-text[^"]*"[^>]*>\s*([^<]+)\s*<', raw)
    criteria = [c.strip() for c in criteria]

    # Salary — sits in a <div class="salary compensation__salary">
    salary_raw = first(r'class="salary compensation__salary"[^>]*>\s*([^<]+)\s*<')
    salary = re.sub(r"\s+", " ", salary_raw).strip() if salary_raw else None

    title = first(r'class="top-card-layout__title[^"]*"[^>]*>([^<]+)<')
    company = first(r'class="topcard__org-name-link[^"]*"[^>]*>\s*([^<]+)\s*<')
    location = first(r'class="topcard__flavor topcard__flavor--bullet"[^>]*>\s*([^<]+)\s*<')

    job = {
        "job_posting_id": job_id,
        "job_url": canonical_url,
        "apply_link": canonical_url,
        "job_title": title,
        "company_name": company,
        "job_location": location,
        "job_base_pay_range": salary,
        "job_description": description,
        "job_seniority_level": criteria[0] if len(criteria) > 0 else None,
        "job_employment_type": criteria[1] if len(criteria) > 1 else None,
        "job_function": criteria[2] if len(criteria) > 2 else None,
        "job_industries": criteria[3] if len(criteria) > 3 else None,
        "source": "linkedin",
    }

    print(f"Retrieved: {job.get('job_title')} @ {job.get('company_name')}")
    return job


def scrape_ziprecruiter(job_url: str) -> dict:
    """Uses Playwright headless Chromium to scrape a ZipRecruiter job page.
    Handles both redirect share URLs and direct /jobs/v2/<token> URLs.
    """
    from playwright.sync_api import sync_playwright
    import base64

    print(f"Scraping ZipRecruiter job: {job_url}")

    with sync_playwright() as p:
        browser = p.chromium.launch(headless=True)
        page = browser.new_page(
            user_agent=(
                "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) "
                "AppleWebKit/537.36 (KHTML, like Gecko) "
                "Chrome/124.0.0.0 Safari/537.36"
            )
        )
        page.goto(job_url, wait_until="domcontentloaded", timeout=30_000)

        # Dismiss login modal if present
        try:
            page.keyboard.press("Escape")
            page.wait_for_timeout(800)
        except Exception:
            pass

        # Wait for job title to appear
        page.wait_for_selector("h2", timeout=15_000)

        job = page.evaluate("""() => {
            // Extract listing_key from base64 token in URL path
            const pathMatch = window.location.pathname.match(/\\/jobs\\/v2\\/([^?/]+)/);
            let listing_key = null;
            if (pathMatch) {
                try {
                    const decoded = JSON.parse(atob(pathMatch[1]));
                    listing_key = decoded.listing_key ?? null;
                } catch (e) {}
            }

            // Title: first h2 with font-bold class (the job title heading)
            const titleEl = document.querySelector('h2[class*="font-bold"]');
            const title = titleEl?.innerText?.trim() ?? null;

            // Company: bold link near the title area
            const companyEl = document.querySelector('a[class*="text-link"][class*="font-bold"], a[class*="font-bold"][class*="text-link"]');
            const company = companyEl?.innerText?.trim() ?? null;

            // Find the "Job description" heading to get description text
            const allEls = Array.from(document.querySelectorAll('*'));
            const descHeading = allEls.find(el =>
                el.children.length === 0 &&
                el.innerText?.trim() === 'Job description'
            );
            const descSection = descHeading?.parentElement?.parentElement;
            let description = descSection?.innerText?.trim() ?? null;
            if (description?.startsWith('Job description\\n')) {
                description = description.slice('Job description\\n'.length).trim();
            }

            // Salary, location, employment_type — scan page text for labelled items
            // ZipRecruiter puts these in the sidebar/header as text nodes
            const bodyText = document.body.innerText;

            // Look for salary pattern: $NNK - $NNK/yr or $NN/hr etc.
            const salaryMatch = bodyText.match(/\\$(\\d[\\d,KkMm]*(?:\\.\\d+)?\\s*(?:-\\s*\\$[\\d,KkMm]*(?:\\.\\d+)?)?\\s*\\/(?:yr|hr|hour|year|mo|month))/i);
            const salary = salaryMatch ? salaryMatch[0].trim() : null;

            // Location: look for city/state pattern near "On-site", "Remote", "Hybrid"
            const locationMatch = bodyText.match(/([A-Za-z ]+,\\s*[A-Z]{2})\\s*[•·]\\s*(On-site|Remote|Hybrid)/i);
            const location = locationMatch
                ? `${locationMatch[1].trim()} • ${locationMatch[2].trim()}`
                : (bodyText.match(/\\b(Remote|Hybrid)\\b/i)?.[0] ?? null);

            // Employment type: look for known types
            const empMatch = bodyText.match(/\\b(Full[- ]Time|Part[- ]Time|Contract(?:or)?|Temporary|Internship|Freelance)\\b/i);
            const employment_type = empMatch ? empMatch[0].trim() : null;

            return {
                job_id: listing_key,
                url: window.location.href,
                apply_link: window.location.href,
                title,
                company_name: company,
                location,
                salary,
                employment_type,
                description,
                source: 'ziprecruiter',
            };
        }""")

        browser.close()

    print(f"Retrieved: {job.get('title')} @ {job.get('company_name')}")
    return job


def scrape_indeed(job_url: str) -> dict:
    """Uses Playwright headless Chromium to scrape an Indeed job page."""
    from playwright.sync_api import sync_playwright

    # Normalise to just ?jk=<id> — avoids tracking params causing redirects
    parsed = urlparse(job_url)
    jk = parse_qs(parsed.query).get("jk", [None])[0]
    if not jk:
        print("ERROR: Could not extract job key (jk) from Indeed URL.")
        sys.exit(1)
    clean_url = urlunparse(parsed._replace(query=f"jk={jk}"))
    print(f"Scraping Indeed job: {clean_url}")

    with sync_playwright() as p:
        browser = p.chromium.launch(headless=True)
        page = browser.new_page(
            user_agent=(
                "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) "
                "AppleWebKit/537.36 (KHTML, like Gecko) "
                "Chrome/124.0.0.0 Safari/537.36"
            )
        )
        page.goto(clean_url, wait_until="domcontentloaded", timeout=30_000)
        page.wait_for_selector("#jobDescriptionText", timeout=15_000)

        job = page.evaluate("""() => {
            const jk = new URLSearchParams(window.location.search).get('jk');
            const salaryRaw = document.querySelector('#salaryInfoAndJobType')?.innerText?.trim() ?? null;
            // Split "salary - employment_type" — Indeed puts them in one element
            let salary = salaryRaw, employment_type = null;
            if (salaryRaw) {
                const parts = salaryRaw.split(' - ');
                employment_type = parts.length > 1 ? parts[parts.length - 1].trim() : null;
                salary = parts.length > 1 ? parts.slice(0, -1).join(' - ').trim() : salaryRaw;
            }
            return {
                job_id:          jk,
                url:             `https://www.indeed.com/viewjob?jk=${jk}`,
                apply_link:      `https://www.indeed.com/viewjob?jk=${jk}`,
                title:           document.querySelector('h1[data-testid="jobsearch-JobInfoHeader-title"], h1')?.innerText?.trim() ?? null,
                company_name:    document.querySelector('[data-testid="inlineHeader-companyName"] a, [data-testid="inlineHeader-companyName"]')?.innerText?.trim() ?? null,
                location:        document.querySelector('[data-testid="inlineHeader-companyLocation"]')?.innerText?.trim() ?? null,
                salary:          salary,
                employment_type: employment_type,
                description:     document.querySelector('#jobDescriptionText')?.innerText?.trim() ?? null,
                source:          'indeed',
            };
        }""")

        browser.close()

    print(f"Retrieved: {job.get('title')} @ {job.get('company_name')}")
    return job


def _parse_jsonld_job(job_url: str, source: str) -> dict:
    """Shared JSON-LD JobPosting extractor for sites that embed schema.org structured data."""
    resp = requests.get(
        job_url,
        headers={"User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36"},
        timeout=30,
    )
    resp.raise_for_status()
    resp.encoding = "utf-8"
    raw = resp.text

    blobs = re.findall(r'<script[^>]+type=["\']application/ld\+json["\'][^>]*>(.*?)</script>', raw, re.DOTALL)
    posting = None
    for blob in blobs:
        try:
            data = json.loads(blob)
            # Handle both bare object and @graph array
            candidates = data if isinstance(data, list) else [data]
            for item in candidates:
                if isinstance(item, dict) and item.get("@type") == "JobPosting":
                    posting = item
                    break
        except json.JSONDecodeError:
            continue
        if posting:
            break

    if not posting:
        print(f"ERROR: No JobPosting JSON-LD found on {job_url}")
        sys.exit(1)

    # Strip HTML tags from description
    desc_html = posting.get("description", "")
    desc_text = re.sub(r"<[^>]+>", " ", desc_html)
    desc_text = html.unescape(desc_text)
    desc_text = re.sub(r"\s{2,}", "\n", desc_text).strip()

    # Employment type
    emp_raw = posting.get("employmentType", "")
    if isinstance(emp_raw, list):
        emp_raw = emp_raw[0] if emp_raw else ""
    employment_type = emp_raw.replace("_", "-").title() if emp_raw else None

    # Location
    if posting.get("jobLocationType") == "TELECOMMUTE":
        location = "Remote"
    else:
        loc = posting.get("jobLocation", {})
        if isinstance(loc, list):
            loc = loc[0] if loc else {}
        addr = loc.get("address", {}) if isinstance(loc, dict) else {}
        location = addr.get("addressLocality") or addr.get("addressRegion") or addr.get("addressCountry") or None

    # Salary from baseSalary schema
    salary = None
    bs = posting.get("baseSalary", {})
    if bs:
        val = bs.get("value", {})
        currency = bs.get("currency", "USD")
        symbol = "$" if currency == "USD" else currency + " "
        unit = val.get("unitText", "YEAR")
        suffix = "/yr" if unit == "YEAR" else "/hr"

        def fmt(n):
            n = int(n)
            return f"{symbol}{n // 1000}K" if n >= 1000 and n % 1000 == 0 else f"{symbol}{n:,}"

        lo, hi = val.get("minValue"), val.get("maxValue")
        if lo and hi:
            salary = f"{fmt(lo)} - {fmt(hi)}{suffix}"
        elif lo:
            salary = f"{fmt(lo)}{suffix}"
        elif hi:
            salary = f"{fmt(hi)}{suffix}"

    # Apply link: prefer first non-site external link found in raw HTML near "apply"
    domain = urlparse(job_url).netloc.lstrip("www.")
    apply_candidates = re.findall(
        rf'href="(https?://(?!(?:www\.)?{re.escape(domain)})[^"]+)"[^>]*>\s*(?:Apply|APPLY)',
        raw, re.IGNORECASE
    )
    apply_link = html.unescape(apply_candidates[0]) if apply_candidates else job_url

    # job_id from URL path last segment or identifier
    path_parts = urlparse(job_url).path.rstrip("/").split("/")
    job_id = path_parts[-1] if path_parts else None
    if not job_id:
        job_id = posting.get("identifier", {}).get("value")

    org = posting.get("hiringOrganization", {})
    # Clean title (some sites prefix with "[Remote] " etc.)
    title = re.sub(r"^\[.*?\]\s*", "", posting.get("title", "")).strip()

    return {
        "job_id": job_id,
        "url": job_url,
        "apply_link": apply_link,
        "title": title,
        "company_name": org.get("name"),
        "company_website": org.get("sameAs"),
        "location": location,
        "salary": salary,
        "employment_type": employment_type,
        "description": desc_text,
        "source": source,
    }


def scrape_handshake(job_url: str) -> dict:
    """Extracts job data from Handshake's JSON-LD JobPosting schema via plain HTTP."""
    print(f"Scraping Handshake job: {job_url}")
    job = _parse_jsonld_job(job_url, source="handshake")
    # Title in JSON-LD includes " | Company | Handshake" suffix — strip it
    if job.get("title"):
        job["title"] = re.split(r"\s*\|\s*", job["title"])[0].strip()
    # Apply link may be embedded in the description as a URL on its own line
    if job.get("description") and job.get("apply_link") == job_url:
        match = re.search(r"https?://(?!(?:www\.)?joinhandshake\.com|app\.joinhandshake\.com)[^\s<\"]+", job["description"])
        if match:
            job["apply_link"] = match.group(0).rstrip(".")
    print(f"Retrieved: {job.get('title')} @ {job.get('company_name')}")
    return job


def scrape_jobright(job_url: str) -> dict:
    """Extracts job data from Jobright.ai's JSON-LD JobPosting schema."""
    print(f"Scraping Jobright job: {job_url}")
    job = _parse_jsonld_job(job_url, source="jobright")
    print(f"Retrieved: {job.get('title')} @ {job.get('company_name')}")
    return job


def scrape_jobgether(job_url: str) -> dict:
    """Extracts job data from Jobgether's JSON-LD JobPosting schema via plain HTTP."""
    print(f"Scraping Jobgether job: {job_url}")
    job = _parse_jsonld_job(job_url, source="jobgether")
    # Drop Jobgether's attribution footer from description
    if job.get("description"):
        job["description"] = re.sub(
            r"This offer from .* Jobgether\.com.*", "", job["description"], flags=re.DOTALL
        ).strip()
    print(f"Retrieved: {job.get('title')} @ {job.get('company_name')}")
    return job


# ---------------------------------------------------------------------------
# Router
# ---------------------------------------------------------------------------

HANDLERS = {
    "linkedin.com": scrape_linkedin,
    "www.linkedin.com": scrape_linkedin,
    "indeed.com": scrape_indeed,
    "www.indeed.com": scrape_indeed,
    "ziprecruiter.com": scrape_ziprecruiter,
    "www.ziprecruiter.com": scrape_ziprecruiter,
    "jobgether.com": scrape_jobgether,
    "www.jobgether.com": scrape_jobgether,
    "jobright.ai": scrape_jobright,
    "www.jobright.ai": scrape_jobright,
    "app.joinhandshake.com": scrape_handshake,
    "joinhandshake.com": scrape_handshake,
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
