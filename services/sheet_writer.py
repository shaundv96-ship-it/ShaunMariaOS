"""
ShaunMariaOS

Google Sheets Writer
"""

from typing import Any

from googleapiclient.discovery import build
from googleapiclient.errors import HttpError

from apps.google_engine import get_google_credentials
from config import GOOGLE_SHEET_ID


def get_sheet_service():
    """Return an authenticated Google Sheets service."""
    credentials = get_google_credentials()

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

def update_cells(
    sheet_name: str,
    cell_updates: dict[str, Any],
) -> dict:
    """
    Update specific cells in a Google Sheets worksheet.

    Example:
        {
            "E3": 3600,
            "J3": "14 July 2026",
        }
    """

    if not sheet_name.strip():
        raise ValueError("Sheet name cannot be empty.")

    if not cell_updates:
        raise ValueError("Cell updates cannot be empty.")

    try:
        service = get_sheet_service()

        data = [
            {
                "range": f"'{sheet_name}'!{cell}",
                "values": [[value]],
            }
            for cell, value in cell_updates.items()
        ]

        result = (
            service.spreadsheets()
            .values()
            .batchUpdate(
                spreadsheetId=GOOGLE_SHEET_ID,
                body={
                    "valueInputOption": "USER_ENTERED",
                    "data": data,
                },
            )
            .execute()
        )

        return {
            "success": True,
            "updated_cells": result.get(
                "totalUpdatedCells",
                0,
            ),
        }

    except HttpError as error:
        raise RuntimeError(
            f"Google Sheets update failed: {error}"
        ) from error