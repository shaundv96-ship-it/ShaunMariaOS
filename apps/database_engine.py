"""
ShaunMariaOS

Database Engine
Provides access to Google Sheets worksheets.
"""

from apps.sheets_engine import get_spreadsheet, get_worksheet_values
from constants import (
    BUDGET_SHEET,
    CHECKLIST_SHEET,
    GUESTLIST_SHEET,
    HENNA_PARTY_SHEET,
    HONEYMOON_SHEET,
    PHOTOGRAPHY_SHEET,
    SEATING_PLAN_SHEET,
    STD_SHEET,
    TIMELINE_SHEET,
    WEDDING_PARTY_SHEET,
)


FINANCE_SHEET = "Finance"


def get_database_status():
    """Return the Google Sheets database connection status."""
    spreadsheet = get_spreadsheet()
    worksheets = spreadsheet.worksheets()

    lines = [
        "❤️ <b>ShaunMariaOS Database</b>",
        "",
        "🟢 <b>Status</b>",
        "Connected",
        "",
        "📄 <b>Database</b>",
        spreadsheet.title,
        "",
        "📚 <b>Available Tabs</b>",
    ]

    lines.extend(f"• {worksheet.title}" for worksheet in worksheets)

    lines.extend(
        [
            "",
            "✅ Live via Google Sheets",
        ]
    )

    return "\n".join(lines)


# ====================================================
# Wedding Sheets
# ====================================================

def get_budget_sheet():
    return get_worksheet_values(BUDGET_SHEET)


def get_checklist_sheet():
    return get_worksheet_values(CHECKLIST_SHEET)


def get_guestlist_sheet():
    return get_worksheet_values(GUESTLIST_SHEET)


def get_std_sheet():
    return get_worksheet_values(STD_SHEET)


def get_wedding_party_sheet():
    return get_worksheet_values(WEDDING_PARTY_SHEET)


def get_henna_party_sheet():
    return get_worksheet_values(HENNA_PARTY_SHEET)


def get_seating_plan_sheet():
    return get_worksheet_values(SEATING_PLAN_SHEET)


def get_photography_sheet():
    return get_worksheet_values(PHOTOGRAPHY_SHEET)


def get_timeline_sheet():
    return get_worksheet_values(TIMELINE_SHEET)


def get_honeymoon_sheet():
    return get_worksheet_values(HONEYMOON_SHEET)


# ====================================================
# Finance Sheets
# ====================================================

def get_finance_sheet():
    return get_worksheet_values(FINANCE_SHEET)