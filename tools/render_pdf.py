#!/usr/bin/env python3
"""
Renders tailored HTML resume and cover letter files to PDF using Playwright.
Scans .data/output/{today}/ for all HTML files and renders each to PDF alongside it.
Ensures text is selectable/copiable (vector PDF, not image-based).

Usage:
  .venv/bin/python tools/render_pdf.py             # renders today's output
  .venv/bin/python tools/render_pdf.py 2026-07-15  # renders a specific date
"""

import sys
from datetime import datetime, timezone
from pathlib import Path

from playwright.sync_api import sync_playwright

DATA_DIR = Path(__file__).parent.parent / ".data"
PACK_DIR = Path(__file__).parent.parent / "application-pack"

PAGE_SIZES = {
    "letter": {"width": "8.5in", "height": "11in"},
    "a4":     {"width": "210mm", "height": "297mm"},
}


def detect_page_size(html: str) -> dict:
    if 'size="a4"' in html or "size='a4'" in html:
        return PAGE_SIZES["a4"]
    return PAGE_SIZES["letter"]


def slugify(text: str) -> str:
    return "-".join("".join(c if c.isalnum() or c == " " else "" for c in text.lower()).split())


def pdf_filename(html_path: Path) -> str:
    parent = html_path.parent.name  # e.g. 4437324526_Walt_Disney_Company
    parts = parent.split("_", 1)
    company_slug = slugify(parts[1]) if len(parts) > 1 else "company"
    job_dir = html_path.parent
    # Detect title from sibling metadata if present, else use stem
    title_file = job_dir / "title.txt"
    position_slug = slugify(title_file.read_text().strip()) if title_file.exists() else ""
    suffix = f"-{position_slug}" if position_slug else ""

    if "cover" in html_path.stem.lower():
        return f"jaime-nguyen-cover-letter-{company_slug}{suffix}.pdf"
    return f"jaime-nguyen-resume-{company_slug}{suffix}.pdf"


def render_html_to_pdf(page, html_path: Path) -> Path:
    pdf_path = html_path.parent / pdf_filename(html_path)
    html = html_path.read_text(encoding="utf-8")
    size = detect_page_size(html)

    page.goto(f"file://{html_path.resolve()}", wait_until="load")
    page.wait_for_timeout(2500)  # Wait for web components + fonts

    page.pdf(
        path=str(pdf_path),
        width=size["width"],
        height=size["height"],
        print_background=True,
        margin={"top": "0", "right": "0", "bottom": "0", "left": "0"},
    )
    return pdf_path


def main():
    date_str = sys.argv[1] if len(sys.argv) > 1 else datetime.now(timezone.utc).strftime("%Y-%m-%d")
    output_dir = DATA_DIR / "output" / date_str

    if not output_dir.exists():
        print(f"ERROR: Output directory not found: {output_dir}")
        print("Run prepare_application_pack.py first and have the agent generate the HTML files.")
        sys.exit(1)

    html_files = sorted(output_dir.rglob("*.html"))
    if not html_files:
        print(f"No HTML files found in {output_dir}")
        sys.exit(0)

    print(f"Found {len(html_files)} HTML file(s) to render in {output_dir}\n")

    with sync_playwright() as p:
        browser = p.chromium.launch(headless=True)
        context = browser.new_context()

        # Grant access to local files in the application-pack dir
        page = context.new_page()

        for html_path in html_files:
            print(f"Rendering: {html_path.relative_to(DATA_DIR)}")
            try:
                pdf_path = render_html_to_pdf(page, html_path)
                print(f"  → {pdf_path.relative_to(DATA_DIR)}")
            except Exception as e:
                print(f"  ERROR: {e}")

        browser.close()

    print(f"\nDone. PDFs saved to {output_dir}")


if __name__ == "__main__":
    main()
