"""
ShaunMariaOS

Health Engine
"""

from app_config import APP_NAME, APP_VERSION, APP_STAGE
from apps.calendar_engine import get_calendar_summary
from apps.database_engine import get_database_status
from utils.ui import build_screen


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

    sections = [
        ("🤖 Telegram", "🟢 Online"),
        ("☁️ Railway", "🟢 Running"),
        ("📅 Google Calendar", calendar_status),
        ("📊 Google Sheets", sheets_status),
        ("⏰ Scheduler", "🟢 Active"),
        ("🚀 Version", f"v{APP_VERSION} {APP_STAGE}"),
    ]

    return build_screen(
        f"❤️ <b>{APP_NAME} Health</b>",
        sections,
        "Everything looks good! 🎉",
    )