"""
ShaunMariaOS

Health Engine
"""

from app_config import APP_NAME, APP_VERSION, APP_STAGE
from apps.calendar_engine import get_calendar_summary
from apps.database_engine import get_database_status


def get_health():
    calendar_status = "🟢 Connected"
    sheets_status = "🟢 Connected"

    try:
        get_calendar_summary()
    except Exception:
        calendar_status = "🔴 Unavailable"

    try:
        get_database_status()
    except Exception:
        sheets_status = "🔴 Unavailable"

    return f"""❤️ <b>{APP_NAME} Health</b>

🤖 <b>Telegram</b>
🟢 Online

☁️ <b>Railway</b>
🟢 Running

📅 <b>Google Calendar</b>
{calendar_status}

📊 <b>Google Sheets</b>
{sheets_status}

⏰ <b>Scheduler</b>
🟢 Active

🚀 <b>Version</b>
v{APP_VERSION} {APP_STAGE}"""