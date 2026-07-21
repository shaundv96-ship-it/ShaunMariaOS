"""
ShaunMariaOS

Google Sheets Engine
"""

import time
from threading import RLock
from typing import Any

import gspread

from apps.google_engine import get_google_credentials
from config import GOOGLE_SHEET_ID


# ==========================================================
# Cache Configuration
# ==========================================================

WORKSHEET_CACHE_TTL_SECONDS = 60


# ==========================================================
# In-Memory Cache
# ==========================================================

_sheets_client: gspread.Client | None = None
_spreadsheet: Any | None = None

_worksheet_cache: dict[str, dict[str, Any]] = {}

_cache_lock = RLock()


# ==========================================================
# Google Sheets
# ==========================================================

def get_sheets_client() -> gspread.Client:
    """
    Return one authenticated gspread client.

    The client is reused for the lifetime of the current bot process.
    """

    global _sheets_client

    with _cache_lock:
        if _sheets_client is None:
            credentials = get_google_credentials()
            _sheets_client = gspread.authorize(credentials)

        return _sheets_client


def get_spreadsheet():
    """
    Open and return the ShaunMariaOS spreadsheet.

    The spreadsheet object is cached so repeated worksheet reads do not
    repeatedly call open_by_key().
    """

    global _spreadsheet

    if not GOOGLE_SHEET_ID:
        raise ValueError(
            "GOOGLE_SHEET_ID environment variable is missing."
        )

    with _cache_lock:
        if _spreadsheet is None:
            client = get_sheets_client()
            _spreadsheet = client.open_by_key(
                GOOGLE_SHEET_ID
            )

        return _spreadsheet


def list_sheet_names() -> list[str]:
    """Return all worksheet names."""

    spreadsheet = get_spreadsheet()

    return [
        worksheet.title
        for worksheet in spreadsheet.worksheets()
    ]


def get_worksheet_values(
    sheet_name: str,
    *,
    force_refresh: bool = False,
) -> list[list[str]]:
    """
    Return every populated value from a worksheet.

    Worksheet values are cached briefly to prevent repeated Google Sheets
    reads when DashboardOS, AdvisorOS, BriefingOS, and other modules request
    the same data within a short period.
    """

    if not sheet_name:
        raise ValueError(
            "A worksheet name must be provided."
        )

    now = time.monotonic()

    with _cache_lock:
        cached = _worksheet_cache.get(sheet_name)

        if (
            not force_refresh
            and cached is not None
            and now - cached["timestamp"]
            < WORKSHEET_CACHE_TTL_SECONDS
        ):
            return cached["values"]

    spreadsheet = get_spreadsheet()
    worksheet = spreadsheet.worksheet(sheet_name)
    values = worksheet.get_all_values()

    with _cache_lock:
        _worksheet_cache[sheet_name] = {
            "timestamp": time.monotonic(),
            "values": values,
        }

    return values


def clear_worksheet_cache(
    sheet_name: str | None = None,
) -> None:
    """
    Clear cached worksheet values.

    Pass a worksheet name to clear one sheet, or omit it to clear all sheets.
    """

    with _cache_lock:
        if sheet_name is None:
            _worksheet_cache.clear()
        else:
            _worksheet_cache.pop(
                sheet_name,
                None,
            )


def reset_sheets_connection() -> None:
    """
    Clear the cached Google Sheets client, spreadsheet, and worksheet data.

    Useful after an authentication problem or during local testing.
    """

    global _sheets_client
    global _spreadsheet

    with _cache_lock:
        _sheets_client = None
        _spreadsheet = None
        _worksheet_cache.clear()


# ==========================================================
# Testing
# ==========================================================

if __name__ == "__main__":
    print("Available Sheets:")

    for sheet_name in list_sheet_names():
        print("-", sheet_name)