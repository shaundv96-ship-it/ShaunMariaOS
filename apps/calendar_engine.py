"""
Shaun&Maria OS
Calendar Engine
"""

from datetime import datetime, timedelta, timezone
from pathlib import Path

from google.auth.transport.requests import Request
from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import InstalledAppFlow
from googleapiclient.discovery import build
import sys
from pathlib import Path

BASE_DIR = Path(__file__).resolve().parent.parent
sys.path.append(str(BASE_DIR))
from config import GOOGLE_CALENDAR_ID

SCOPES = ["https://www.googleapis.com/auth/calendar.readonly"]

BASE_DIR = Path(__file__).resolve().parent.parent
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


def get_today_events():
    service = get_calendar_service()

    now = datetime.now(timezone.utc)
    end_of_day = now.replace(hour=15, minute=59, second=59, microsecond=0)

    events_result = (
        service.events()
        .list(
            calendarId=GOOGLE_CALENDAR_ID,
            timeMin=now.isoformat(),
            timeMax=end_of_day.isoformat(),
            singleEvents=True,
            orderBy="startTime",
        )
        .execute()
    )

    return events_result.get("items", [])


if __name__ == "__main__":

    events = get_today_events()

    print()
    print("=" * 45)
    print("❤️ Shaun&Maria OS")
    print("📅 Today's Schedule")
    print("=" * 45)

    if not events:
        print("🎉 No events today!")
    else:

        for i, event in enumerate(events, start=1):

            start = event["start"].get(
                "dateTime",
                event["start"].get("date")
            )

            title = event.get("summary", "Untitled Event")

            print()
            print(f"{i}. {title}")
            print(f"   🕒 {start}")

    print()
    print("=" * 45)