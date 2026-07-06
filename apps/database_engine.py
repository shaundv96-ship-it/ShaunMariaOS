"""
ShaunMariaOS

Database Engine
"""

from apps.sheets_engine import get_spreadsheet, get_worksheet_values
from constants import (
    BUDGET_SHEET,
    CHECKLIST_SHEET,
    GUESTLIST_SHEET,
    STD_SHEET,
    WEDDING_PARTY_SHEET,
    HENNA_PARTY_SHEET,
    SEATING_PLAN_SHEET,
    PHOTOGRAPHY_SHEET,
    TIMELINE_SHEET,
    HONEYMOON_SHEET,
)


def get_database_status():
    spreadsheet = get_spreadsheet()
    worksheets = spreadsheet.worksheets()

    message = "❤️ <b>ShaunMariaOS Database</b>\n\n"
    message += "🟢 <b>Status</b>\nConnected\n\n"
    message += f"📄 <b>Database</b>\n{spreadsheet.title}\n\n"
    message += "📚 <b>Available Tabs</b>\n"

    for sheet in worksheets:
        message += f"• {sheet.title}\n"

    message += "\n✅ Live via Google Sheets"
    return message


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

def debug_timeline_sheet():
    rows = get_timeline_sheet()

    print("\n===== TIMELINE SHEET =====\n")

    for i, row in enumerate(rows):
        print(i, row)

if __name__ == "__main__":
    debug_timeline_sheet()