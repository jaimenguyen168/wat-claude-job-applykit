#!/usr/bin/env python3
"""
Uploads the single job's PDFs to Google Drive and logs a row to the tracking sheet.
Reads from single_job_result.json and .data/output/single/.
Schema-agnostic — uses _get() to handle any provider's field names.

Usage: .venv/bin/python tools/upload_single_job.py
"""

import json
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent))
from google.auth.transport.requests import Request
from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import InstalledAppFlow
from googleapiclient.discovery import build
from googleapiclient.http import MediaFileUpload

from constants.google_config import (
    DRIVE_JOBS_FOLDER_ID,
    SHEET_NAME,
    SPREADSHEET_ID,
)

ROOT_DIR = Path(__file__).parent.parent
DATA_DIR = ROOT_DIR / ".data"
SINGLE_JOB_FILE = DATA_DIR / "single_job_result.json"
OUTPUT_DIR = DATA_DIR / "output" / "single"
CREDENTIALS_FILE = ROOT_DIR / "credentials.json"
TOKEN_FILE = ROOT_DIR / "token.json"

SCOPES = [
    "https://www.googleapis.com/auth/drive",
    "https://www.googleapis.com/auth/spreadsheets",
]


def _get(job: dict, *keys: str, default=""):
    for k in keys:
        v = job.get(k)
        if v is not None:
            return v
    return default


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


def find_pdfs(job_dir: Path) -> tuple[Path | None, Path | None]:
    resume_pdf = next((f for f in job_dir.glob("*.pdf") if "cover" not in f.name.lower()), None)
    cover_pdf = next((f for f in job_dir.glob("*.pdf") if "cover" in f.name.lower()), None)
    return resume_pdf, cover_pdf


def append_row(sheets, job: dict, resume_link: str, cover_letter_link: str):
    row = [
        _get(job, "apply_link", "job_url", "applyUrl", "link", "url"),
        job.get("score", ""),
        _get(job, "job_title", "title"),
        _get(job, "company_name", "companyName"),
        _get(job, "company_linkedin_url", "companyLinkedinUrl", "company_url"),
        _get(job, "job_base_pay_range", "salary"),
        (_get(job, "job_description", "descriptionText", "description") or "")[:50000],
        _get(job, "job_location", "location"),
        _get(job, "job_seniority_level", "seniorityLevel", "seniority_level"),
        _get(job, "job_employment_type", "employmentType", "employment_type"),
        _get(job, "job_industries", "industries"),
        _get(job, "company_website", "companyWebsite"),
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


def main():
    if not SINGLE_JOB_FILE.exists():
        print("ERROR: single_job_result.json not found — run scrape_single_job.py first")
        sys.exit(1)

    with open(SINGLE_JOB_FILE, encoding="utf-8") as f:
        job = json.load(f)

    if job.get("verdict") != "yes":
        print(f"Job verdict is '{job.get('verdict')}' — skipping upload.")
        sys.exit(0)

    job_id = _get(job, "job_posting_id", "id", "job_id")
    company = _get(job, "company_name", "companyName", default="Unknown")

    job_dirs = list(OUTPUT_DIR.glob(f"{job_id}_*"))
    if not job_dirs:
        print(f"ERROR: No output directory found for job {job_id} in {OUTPUT_DIR}")
        print("Run prepare_single_job_application_pack.py and render_pdf.py single first.")
        sys.exit(1)

    job_dir = job_dirs[0]
    resume_pdf, cover_pdf = find_pdfs(job_dir)

    if not resume_pdf or not cover_pdf:
        print(f"ERROR: Missing PDF(s) in {job_dir.name}")
        sys.exit(1)

    print("Authenticating with Google...")
    drive, sheets = get_google_services()

    title = _get(job, "job_title", "title")
    print(f"\nProcessing: {title} @ {company}")

    folder_id = get_or_create_subfolder(drive, DRIVE_JOBS_FOLDER_ID, company)
    print(f"  Drive folder: Jobs/{company}/")

    resume_link = upload_pdf(drive, folder_id, resume_pdf)
    print(f"  Uploaded resume: {resume_pdf.name}")

    cover_link = upload_pdf(drive, folder_id, cover_pdf)
    print(f"  Uploaded cover letter: {cover_pdf.name}")

    append_row(sheets, job, resume_link, cover_link)
    print("  Logged to spreadsheet")

    print("\nDone.")


if __name__ == "__main__":
    main()
