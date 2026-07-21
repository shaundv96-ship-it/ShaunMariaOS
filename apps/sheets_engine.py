"""
ShaunMariaOS

Google Sheets Engine
"""

import gspread

from apps.google_engine import get_google_credentials
from config import GOOGLE_SHEET_ID


# ==========================================================
# Google Sheets
# ==========================================================

def get_sheets_client():
    """Return an authenticated gspread client."""

    credentials = get_google_credentials()

    return gspread.authorize(credentials)


def get_spreadsheet():
    """Open and return the ShaunMariaOS spreadsheet."""

    if not GOOGLE_SHEET_ID:
        raise ValueError(
            "GOOGLE_SHEET_ID environment variable is missing."
        )

    client = get_sheets_client()

    return client.open_by_key(GOOGLE_SHEET_ID)


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