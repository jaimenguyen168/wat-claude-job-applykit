#!/usr/bin/env python3
"""
For each passed job with generated PDFs:
1. Creates Jobs/{Company Name}/ subfolder in Google Drive (if not exists)
2. Uploads resume and cover letter PDFs
3. Gets shareable links for both
4. Appends a row to the tracking spreadsheet

Usage:
  .venv/bin/python tools/upload_and_log.py
  .venv/bin/python tools/upload_and_log.py 2026-07-15  # specific date
"""

import json
import sys
from datetime import datetime, timezone
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent))
from google.auth.transport.requests import Request
from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import InstalledAppFlow
from googleapiclient.discovery import build
from googleapiclient.http import MediaFileUpload

from constants.google_config import (
    DRIVE_JOBS_FOLDER_ID,
    SHEET_COLUMNS,
    SHEET_NAME,
    SPREADSHEET_ID,
)

ROOT_DIR = Path(__file__).parent.parent
DATA_DIR = ROOT_DIR / ".data"
CREDENTIALS_FILE = ROOT_DIR / "credentials.json"
TOKEN_FILE = ROOT_DIR / "token.json"

SCOPES = [
    "https://www.googleapis.com/auth/drive",
    "https://www.googleapis.com/auth/spreadsheets",
]


def get_google_services():
    creds = None
    if TOKEN_FILE.exists():
        creds = Credentials.from_authorized_user_file(str(TOKEN_FILE), SCOPES)
    if not creds or not creds.valid:
        if creds and creds.expired and creds.refresh_token:
            creds.refresh(Request())
        else:
            flow = InstalledAppFlow.from_client_secrets_file(str(CREDENTIALS_FILE), SCOPES)
            creds = flow.run_local_server(port=0)
        TOKEN_FILE.write_text(creds.to_json())

    drive = build("drive", "v3", credentials=creds)
    sheets = build("sheets", "v4", credentials=creds)
    return drive, sheets


def get_or_create_subfolder(drive, parent_id: str, name: str) -> str:
    query = (
        f"'{parent_id}' in parents and "
        f"name='{name}' and "
        f"mimeType='application/vnd.google-apps.folder' and "
        f"trashed=false"
    )
    results = drive.files().list(q=query, fields="files(id)").execute()
    files = results.get("files", [])
    if files:
        return files[0]["id"]

    folder = drive.files().create(
        body={"name": name, "mimeType": "application/vnd.google-apps.folder", "parents": [parent_id]},
        fields="id",
    ).execute()
    return folder["id"]


def upload_pdf(drive, folder_id: str, pdf_path: Path) -> str:
    media = MediaFileUpload(str(pdf_path), mimetype="application/pdf", resumable=True)
    file = drive.files().create(
        body={"name": pdf_path.name, "parents": [folder_id]},
        media_body=media,
        fields="id",
    ).execute()
    file_id = file["id"]

    drive.permissions().create(
        fileId=file_id,
        body={"type": "anyone", "role": "reader"},
    ).execute()

    return f"https://drive.google.com/file/d/{file_id}/view"


def append_row(sheets, job: dict, resume_link: str, cover_letter_link: str):
    row = [
        job.get("link") or job.get("applyUrl") or "",
        job.get("score", ""),
        job.get("title", ""),
        job.get("companyName", ""),
        job.get("companyLinkedinUrl", ""),
        job.get("salary", ""),
        (job.get("descriptionText") or "")[:50000],
        job.get("location", ""),
        job.get("seniorityLevel", ""),
        job.get("employmentType", ""),
        job.get("industries", ""),
        job.get("companyWebsite", ""),
        resume_link,
        cover_letter_link,
    ]

    sheets.spreadsheets().values().append(
        spreadsheetId=SPREADSHEET_ID,
        range=f"{SHEET_NAME}!A1",
        valueInputOption="USER_ENTERED",
        insertDataOption="INSERT_ROWS",
        body={"values": [row]},
    ).execute()


def find_pdfs(job_dir: Path) -> tuple[Path | None, Path | None]:
    resume_pdf = next((f for f in job_dir.glob("*.pdf") if "cover" not in f.name.lower()), None)
    cover_pdf = next((f for f in job_dir.glob("*.pdf") if "cover" in f.name.lower()), None)
    return resume_pdf, cover_pdf


def load_passed_jobs(date_str: str) -> list:
    jobs_file = DATA_DIR / f"jobs_{date_str}.json"
    if not jobs_file.exists():
        print(f"ERROR: No jobs file for {date_str}")
        sys.exit(1)
    with open(jobs_file, encoding="utf-8") as f:
        return [j for j in json.load(f) if j.get("verdict") == "yes"]


def main():
    date_str = sys.argv[1] if len(sys.argv) > 1 else datetime.now(timezone.utc).strftime("%Y-%m-%d")
    output_dir = DATA_DIR / "output" / date_str

    if not output_dir.exists():
        print(f"ERROR: No output directory found at {output_dir}")
        print("Run prepare_application_pack.py and render_pdf.py first.")
        sys.exit(1)

    passed_jobs = load_passed_jobs(date_str)
    if not passed_jobs:
        print("No passed jobs found. Nothing to upload.")
        sys.exit(0)

    print("Authenticating with Google...")
    drive, sheets = get_google_services()

    for job in passed_jobs:
        job_id = str(job.get("id"))
        company = job.get("companyName", "Unknown")

        job_dirs = list(output_dir.glob(f"{job_id}_*"))
        if not job_dirs:
            print(f"Skipping {company} ({job_id}) — no output directory found")
            continue

        job_dir = job_dirs[0]
        resume_pdf, cover_pdf = find_pdfs(job_dir)

        if not resume_pdf or not cover_pdf:
            print(f"Skipping {company} ({job_id}) — missing PDF(s) in {job_dir.name}")
            continue

        print(f"\nProcessing: {job.get('title')} @ {company}")

        folder_id = get_or_create_subfolder(drive, DRIVE_JOBS_FOLDER_ID, company)
        print(f"  Drive folder: Jobs/{company}/")

        resume_link = upload_pdf(drive, folder_id, resume_pdf)
        print(f"  Uploaded resume: {resume_pdf.name}")

        cover_link = upload_pdf(drive, folder_id, cover_pdf)
        print(f"  Uploaded cover letter: {cover_pdf.name}")

        append_row(sheets, job, resume_link, cover_link)
        print(f"  Logged to spreadsheet")

    print("\nDone.")


if __name__ == "__main__":
    main()
