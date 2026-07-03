"""
ShaunMariaOS
Database Engine
"""

from apps.sheets_engine import get_spreadsheet


def get_database_status():

    spreadsheet = get_spreadsheet()

    worksheets = spreadsheet.worksheets()

    message = "❤️ <b>ShaunMariaOS Database</b>\n\n"

    message += "🟢 <b>Status</b>\n"
    message += "Connected\n\n"

    message += f"📄 <b>Database</b>\n{spreadsheet.title}\n\n"

    message += "📚 <b>Available Tabs</b>\n"

    for sheet in worksheets:
        message += f"• {sheet.title}\n"

    message += "\n✅ Live via Google Sheets"

    return message