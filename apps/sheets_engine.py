"""
ShaunMariaOS
Google Sheets Engine
"""

import sys
from pathlib import Path

BASE_DIR = Path(__file__).resolve().parent.parent
sys.path.append(str(BASE_DIR))

import gspread
from google.auth.transport.requests import Request
from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import InstalledAppFlow

from config import (
    GOOGLE_SHEET_ID,
    SCOPES,
)


CREDENTIALS_FILE = BASE_DIR / "credentials.json"
TOKEN_FILE = BASE_DIR / "token.json"


def get_credentials():
    """
    Return authenticated Google credentials.
    """

    creds = None

    if TOKEN_FILE.exists():
        creds = Credentials.from_authorized_user_file(
            TOKEN_FILE,
            SCOPES,
        )

    if not creds or not creds.valid:

        if creds and creds.expired and creds.refresh_token:
            creds.refresh(Request())

        else:
            flow = InstalledAppFlow.from_client_secrets_file(
                CREDENTIALS_FILE,
                SCOPES,
            )

            creds = flow.run_local_server(port=0)

        TOKEN_FILE.write_text(creds.to_json())

    return creds


def get_sheets_client():
    return gspread.authorize(get_credentials())


def get_spreadsheet():
    client = get_sheets_client()
    return client.open_by_key(GOOGLE_SHEET_ID)


def list_sheet_names():
    spreadsheet = get_spreadsheet()
    return [sheet.title for sheet in spreadsheet.worksheets()]

def get_worksheet_values(sheet_name):
    spreadsheet = get_spreadsheet()
    worksheet = spreadsheet.worksheet(sheet_name)
    return worksheet.get_all_values()

if __name__ == "__main__":
    print("Available sheets:")
    for name in list_sheet_names():
        print("-", name)