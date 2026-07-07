"""
ShaunMariaOS
Calendar Engine
"""

import sys
from datetime import datetime, timedelta, timezone
from pathlib import Path

BASE_DIR = Path(__file__).resolve().parent.parent
sys.path.append(str(BASE_DIR))

from config import GOOGLE_CALENDAR_ID

from google.auth.transport.requests import Request
from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import InstalledAppFlow
from googleapiclient.discovery import build


SCOPES = [
    "https://www.googleapis.com/auth/calendar.readonly",
    "https://www.googleapis.com/auth/spreadsheets.readonly",
    "https://www.googleapis.com/auth/drive.readonly",
]
CREDENTIALS_FILE = BASE_DIR / "credentials.json"
TOKEN_FILE = BASE_DIR / "token.json"


def get_calendar_service():
    creds = None

    if TOKEN_FILE.exists():
        creds = Credentials.from_authorized_user_file(TOKEN_FILE, SCOPES)

    if not creds or not creds.valid:
        if creds and creds.expired and creds.refresh_token:
            creds.refresh(Request())
        else:
            flow = InstalledAppFlow.from_client_secrets_file(
                CREDENTIALS_FILE,
                SCOPES,
            )
            creds = flow.run_local_server(port=0)

        TOKEN_FILE.write_text(creds.to_json())

    return build("calendar", "v3", credentials=creds)


def get_events_between(start_time, end_time):
    service = get_calendar_service()

    events_result = (
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

    return events_result.get("items", [])


def get_today_events():
    now = datetime.now(timezone.utc)
    end_of_day = now.replace(hour=15, minute=59, second=59, microsecond=0)
    return get_events_between(now, end_of_day)


def get_tomorrow_events():
    now = datetime.now(timezone.utc)
    tomorrow = now + timedelta(days=1)

    start_of_tomorrow = tomorrow.replace(hour=0, minute=0, second=0, microsecond=0)
    end_of_tomorrow = tomorrow.replace(hour=23, minute=59, second=59, microsecond=0)

    return get_events_between(start_of_tomorrow, end_of_tomorrow)


def format_events_for_telegram(title, events):
    if not events:
        return f"📅 <b>{title}</b>\n\nNo events scheduled."

    message = f"❤️ <b>ShaunMariaOS</b>\n\n📅 <b>{title}</b>\n\n"

    for event in events:
        event_title = event.get("summary", "Untitled Event")
        start = event["start"].get("dateTime", event["start"].get("date"))

        if "T" in start:
            time_part = start.split("T")[1][:5]
            message += f"🕒 {time_part} - {event_title}\n"
        else:
            message += f"📌 All day - {event_title}\n"

    return message


def format_today_events_for_telegram():
    return format_events_for_telegram("Today's Schedule", get_today_events())


def format_tomorrow_events_for_telegram():
    return format_events_for_telegram("Tomorrow's Schedule", get_tomorrow_events())


if __name__ == "__main__":
    events = get_today_events()
    print(f"Found {len(events)} events today.")

    for event in events:
        print(event.get("summary", "Untitled Event"))

def get_calendar_summary():

    events = get_today_events()

    if not events:
        return {
            "event_count": 0,
            "next_event": "No events today"
        }

    first = events[0]

    title = first.get("summary", "Untitled Event")

    start = first["start"].get(
        "dateTime",
        first["start"].get("date")
    )

    if "T" in start:
        time = start.split("T")[1][:5]
        next_event = f"{title} ({time})"
    else:
        next_event = f"{title} (All Day)"

    return {
        "event_count": len(events),
        "next_event": next_event
    }