"""
ShaunMariaOS
Google Sheets Engine
"""

import json
import os
import sys
from pathlib import Path

BASE_DIR = Path(__file__).resolve().parent.parent
sys.path.append(str(BASE_DIR))

import gspread
from google.auth.transport.requests import Request
from google.oauth2.credentials import Credentials as UserCredentials
from google.oauth2.service_account import Credentials as ServiceCredentials
from google_auth_oauthlib.flow import InstalledAppFlow

from config import (
    GOOGLE_SHEET_ID,
    SHEETS_SCOPES,
)

CREDENTIALS_FILE = BASE_DIR / "credentials.json"
TOKEN_FILE = BASE_DIR / "token.json"


# ==========================================================
# Authentication
# ==========================================================

def get_local_credentials():
    """
    Desktop OAuth login for local development.
    Creates token.json on first login.
    """

    creds = None

    if TOKEN_FILE.exists():
        creds = UserCredentials.from_authorized_user_file(
            TOKEN_FILE,
            SHEETS_SCOPES,
        )

    if creds and creds.expired and creds.refresh_token:
        creds.refresh(Request())

    if not creds or not creds.valid:

        flow = InstalledAppFlow.from_client_secrets_file(
            str(CREDENTIALS_FILE),
            SHEETS_SCOPES,
        )

        creds = flow.run_local_server(port=0)

        TOKEN_FILE.write_text(
            creds.to_json(),
            encoding="utf-8",
        )

    return creds


def get_credentials():
    """
    Railway:
        Uses GOOGLE_SERVICE_ACCOUNT_JSON

    Local:
        Uses OAuth login (token.json)
    """

    service_account_json = os.getenv(
        "GOOGLE_SERVICE_ACCOUNT_JSON"
    )

    if service_account_json:

        print("Using Railway Service Account")

        credentials_info = json.loads(
            service_account_json
        )

        return ServiceCredentials.from_service_account_info(
            credentials_info,
            scopes=SCOPES,
        )

    print("Using Local OAuth Login")

    return get_local_credentials()


# ==========================================================
# Google Sheets
# ==========================================================

def get_sheets_client():
    return gspread.authorize(get_credentials())


def get_spreadsheet():
    client = get_sheets_client()
    return client.open_by_key(GOOGLE_SHEET_ID)


def list_sheet_names():
    spreadsheet = get_spreadsheet()
    return [
        worksheet.title
        for worksheet in spreadsheet.worksheets()
    ]


def get_worksheet_values(sheet_name):
    spreadsheet = get_spreadsheet()
    worksheet = spreadsheet.worksheet(sheet_name)
    return worksheet.get_all_values()


# ==========================================================
# Testing
# ==========================================================

if __name__ == "__main__":

    print("Available Sheets")

    for sheet in list_sheet_names():
        print("-", sheet)