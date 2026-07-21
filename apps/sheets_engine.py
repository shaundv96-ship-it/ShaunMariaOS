"""
ShaunMariaOS
Google Sheets Engine
"""

import json
import os
import sys
from pathlib import Path

import gspread
from google.auth.transport.requests import Request
from google.oauth2.credentials import Credentials as UserCredentials
from google.oauth2.service_account import Credentials as ServiceCredentials
from google_auth_oauthlib.flow import InstalledAppFlow


BASE_DIR = Path(__file__).resolve().parent.parent

if str(BASE_DIR) not in sys.path:
    sys.path.append(str(BASE_DIR))


from config import GOOGLE_SHEET_ID, SHEETS_SCOPES


CREDENTIALS_FILE = BASE_DIR / "credentials.json"
TOKEN_FILE = BASE_DIR / "token.json"


# ==========================================================
# Authentication
# ==========================================================

def get_local_credentials():
    """
    Load desktop OAuth credentials for local development.

    Uses token.json when available.
    Opens a browser only when a new local login is required.
    """

    credentials = None

    if TOKEN_FILE.exists():
        credentials = UserCredentials.from_authorized_user_file(
            str(TOKEN_FILE),
            SHEETS_SCOPES,
        )

    if (
        credentials
        and credentials.expired
        and credentials.refresh_token
    ):
        credentials.refresh(Request())

        TOKEN_FILE.write_text(
            credentials.to_json(),
            encoding="utf-8",
        )

    if not credentials or not credentials.valid:
        if not CREDENTIALS_FILE.exists():
            raise FileNotFoundError(
                "credentials.json was not found for local Google OAuth."
            )

        flow = InstalledAppFlow.from_client_secrets_file(
            str(CREDENTIALS_FILE),
            SHEETS_SCOPES,
        )

        credentials = flow.run_local_server(port=0)

        TOKEN_FILE.write_text(
            credentials.to_json(),
            encoding="utf-8",
        )

    return credentials


def get_service_account_credentials(service_account_json):
    """
    Build Railway service-account credentials from JSON stored
    in GOOGLE_SERVICE_ACCOUNT_JSON.
    """

    try:
        credentials_info = json.loads(service_account_json)
    except json.JSONDecodeError as error:
        raise ValueError(
            "GOOGLE_SERVICE_ACCOUNT_JSON contains invalid JSON."
        ) from error

    required_fields = {
        "type",
        "project_id",
        "private_key",
        "client_email",
        "token_uri",
    }

    missing_fields = required_fields.difference(credentials_info)

    if missing_fields:
        missing_text = ", ".join(sorted(missing_fields))

        raise ValueError(
            "GOOGLE_SERVICE_ACCOUNT_JSON is missing required fields: "
            f"{missing_text}"
        )

    if credentials_info.get("type") != "service_account":
        raise ValueError(
            "GOOGLE_SERVICE_ACCOUNT_JSON is not a service-account key."
        )

    return ServiceCredentials.from_service_account_info(
        credentials_info,
        scopes=SHEETS_SCOPES,
    )


def get_credentials():
    """
    Use service-account authentication on Railway.

    Fall back to desktop OAuth during local development.
    """

    service_account_json = os.getenv(
        "GOOGLE_SERVICE_ACCOUNT_JSON"
    )

    if service_account_json:
        print("Google Sheets authentication: service account")
        return get_service_account_credentials(
            service_account_json
        )

    print("Google Sheets authentication: local OAuth")
    return get_local_credentials()


# ==========================================================
# Google Sheets
# ==========================================================

def get_sheets_client():
    """Return an authenticated gspread client."""

    credentials = get_credentials()
    return gspread.authorize(credentials)


def get_spreadsheet():
    """Open the ShaunMariaOS spreadsheet."""

    if not GOOGLE_SHEET_ID:
        raise ValueError(
            "GOOGLE_SHEET_ID environment variable is missing."
        )

    client = get_sheets_client()

    return client.open_by_key(
        GOOGLE_SHEET_ID
    )


def list_sheet_names():
    """Return all worksheet names."""

    spreadsheet = get_spreadsheet()

    return [
        worksheet.title
        for worksheet in spreadsheet.worksheets()
    ]


def get_worksheet_values(sheet_name):
    """Return every populated value from a worksheet."""

    if not sheet_name:
        raise ValueError(
            "A worksheet name must be provided."
        )

    spreadsheet = get_spreadsheet()
    worksheet = spreadsheet.worksheet(sheet_name)

    return worksheet.get_all_values()


# ==========================================================
# Testing
# ==========================================================

if __name__ == "__main__":
    print("Available Sheets:")

    for sheet_name in list_sheet_names():
        print("-", sheet_name)