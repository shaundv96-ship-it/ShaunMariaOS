"""
ShaunMariaOS

Calendar Engine
"""

from datetime import datetime, timedelta
from pathlib import Path

from google.auth.transport.requests import Request
from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import InstalledAppFlow
from googleapiclient.discovery import build

from config import GOOGLE_CALENDAR_ID
from utils.time import SINGAPORE_TZ, sg_now


BASE_DIR = Path(__file__).resolve().parent.parent
CREDENTIALS_FILE = BASE_DIR / "credentials.json"
TOKEN_FILE = BASE_DIR / "token.json"

SCOPES = [
    "https://www.googleapis.com/auth/calendar.readonly",
    "https://www.googleapis.com/auth/spreadsheets.readonly",
    "https://www.googleapis.com/auth/drive.readonly",
]


def get_calendar_service():
    """Create and return an authenticated Google Calendar service."""
    credentials = None

    if TOKEN_FILE.exists():
        credentials = Credentials.from_authorized_user_file(
            TOKEN_FILE,
            SCOPES,
        )

    if not credentials or not credentials.valid:
        if (
            credentials
            and credentials.expired
            and credentials.refresh_token
        ):
            credentials.refresh(Request())
        else:
            flow = InstalledAppFlow.from_client_secrets_file(
                CREDENTIALS_FILE,
                SCOPES,
            )
            credentials = flow.run_local_server(port=0)

        TOKEN_FILE.write_text(
            credentials.to_json(),
            encoding="utf-8",
        )

    return build(
        "calendar",
        "v3",
        credentials=credentials,
        cache_discovery=False,
    )


def get_events_between(start_time, end_time):
    """Return calendar events occurring within the supplied time range."""
    service = get_calendar_service()

    result = (
        service.events()
        .list(
            calendarId=GOOGLE_CALENDAR_ID,
            timeMin=start_time.isoformat(),
            timeMax=end_time.isoformat(),
            singleEvents=True,
            orderBy="startTime",
        )
        .execute()
    )

    return result.get("items", [])


def get_today_events():
    """Return events from now until the end of today in Singapore."""
    now = sg_now()

    end_of_day = now.replace(
        hour=23,
        minute=59,
        second=59,
        microsecond=999999,
    )

    return get_events_between(now, end_of_day)


def get_tomorrow_events():
    """Return all events scheduled for tomorrow in Singapore."""
    tomorrow = sg_now().date() + timedelta(days=1)

    start_of_tomorrow = datetime.combine(
        tomorrow,
        datetime.min.time(),
        tzinfo=SINGAPORE_TZ,
    )

    end_of_tomorrow = datetime.combine(
        tomorrow,
        datetime.max.time(),
        tzinfo=SINGAPORE_TZ,
    )

    return get_events_between(
        start_of_tomorrow,
        end_of_tomorrow,
    )


def get_event_display_time(event):
    """Return a readable Singapore-time label for an event."""
    start_data = event.get("start", {})
    date_time_text = start_data.get("dateTime")
    date_text = start_data.get("date")

    if date_time_text:
        event_time = datetime.fromisoformat(
            date_time_text.replace("Z", "+00:00")
        ).astimezone(SINGAPORE_TZ)

        return event_time.strftime("%-I:%M %p")

    if date_text:
        return "All day"

    return "Time unavailable"


def format_events_for_telegram(title, events):
    """Format a list of Google Calendar events for Telegram."""
    if not events:
        return f"""📅 <b>{title}</b>

No events scheduled."""

    lines = [
        "❤️ <b>ShaunMariaOS</b>",
        "",
        f"📅 <b>{title}</b>",
        "",
    ]

    for event in events:
        event_title = event.get("summary", "Untitled Event")
        event_time = get_event_display_time(event)

        icon = "📌" if event_time == "All day" else "🕒"
        lines.append(f"{icon} {event_time} — {event_title}")

    return "\n".join(lines)


def format_today_events_for_telegram():
    """Return today's events formatted for Telegram."""
    return format_events_for_telegram(
        "Today's Schedule",
        get_today_events(),
    )


def format_tomorrow_events_for_telegram():
    """Return tomorrow's events formatted for Telegram."""
    return format_events_for_telegram(
        "Tomorrow's Schedule",
        get_tomorrow_events(),
    )


def get_calendar_summary():
    """Return a compact calendar summary for dashboards and advisors."""
    events = get_today_events()

    if not events:
        return {
            "event_count": 0,
            "next_event": "No events scheduled today.",
        }

    next_event = events[0]
    event_title = next_event.get("summary", "Untitled Event")
    event_time = get_event_display_time(next_event)

    return {
        "event_count": len(events),
        "next_event": f"{event_time} — {event_title}",
    }


if __name__ == "__main__":
    today_events = get_today_events()

    print(f"Found {len(today_events)} events today.")

    for calendar_event in today_events:
        title = calendar_event.get("summary", "Untitled Event")
        event_time = get_event_display_time(calendar_event)
        print(f"{event_time} — {title}")