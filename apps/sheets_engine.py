"""
ShaunMariaOS
Google Sheets Engine
"""

import sys
from pathlib import Path
import json
import os

BASE_DIR = Path(__file__).resolve().parent.parent
sys.path.append(str(BASE_DIR))

import gspread
from google.oauth2.credentials import Credentials as UserCredentials
from google.auth.exceptions import RefreshError
from google.auth.transport.requests import Request
from google.oauth2.service_account import Credentials as ServiceCredentials
from google_auth_oauthlib.flow import InstalledAppFlow

from config import (
    GOOGLE_SHEET_ID,
    SCOPES,
)


CREDENTIALS_FILE = BASE_DIR / "credentials.json"
TOKEN_FILE = BASE_DIR / "token.json"


def get_credentials():
    """
    Load Google credentials.

    Railway uses a service account stored in an environment variable.
    Local development may continue using the existing OAuth flow.
    """
    service_account_json = os.getenv("GOOGLE_SERVICE_ACCOUNT_JSON")

    if service_account_json:
        credentials_info = json.loads(service_account_json)

        return Credentials.from_service_account_info(
            credentials_info,
            scopes=SCOPES,
        )

    return get_local_credentials()


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