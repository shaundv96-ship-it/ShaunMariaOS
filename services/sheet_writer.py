"""
ShaunMariaOS

Google Sheets Writer
"""

from typing import Any

from googleapiclient.discovery import build
from googleapiclient.errors import HttpError

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


def append_row(
    sheet_name: str,
    values: list[Any],
) -> dict:
    """
    Append one row to a Google Sheets worksheet.

    Raises:
        ValueError: If the sheet name or row values are missing.
        RuntimeError: If Google Sheets rejects the write.
    """
    if not sheet_name.strip():
        raise ValueError("Sheet name cannot be empty.")

    if not values:
        raise ValueError("Row values cannot be empty.")

    try:
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

        return {
            "success": True,
            "updated_range": result.get(
                "updates",
                {},
            ).get("updatedRange"),
            "updated_rows": result.get(
                "updates",
                {},
            ).get("updatedRows", 0),
        }

    except HttpError as error:
        raise RuntimeError(
            f"Google Sheets write failed: {error}"
        ) from error