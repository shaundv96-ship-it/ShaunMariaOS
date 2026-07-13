"""
ShaunMariaOS

Google Sheets Writer
"""

from googleapiclient.discovery import build

from apps.sheets_engine import get_credentials
from config import GOOGLE_SHEET_ID


def get_sheet_service():
    """Return an authenticated Google Sheets service."""
    credentials = get_credentials()

    return build(
        "sheets",
        "v4",
        credentials=credentials,
        cache_discovery=False,
    )


def append_row(sheet_name, values):
    """Append one row to the selected Google Sheets worksheet."""
    service = get_sheet_service()

    result = (
        service.spreadsheets()
        .values()
        .append(
            spreadsheetId=GOOGLE_SHEET_ID,
            range=f"'{sheet_name}'!A:Z",
            valueInputOption="USER_ENTERED",
            insertDataOption="INSERT_ROWS",
            body={"values": [values]},
        )
        .execute()
    )

    return result