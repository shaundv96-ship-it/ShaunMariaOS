"""
ShaunMariaOS

Calendar Engine
"""

from datetime import datetime, timedelta

from googleapiclient.discovery import build

from apps.google_engine import get_google_credentials
from config import GOOGLE_CALENDAR_ID
from utils.time import SINGAPORE_TZ, sg_now
from apps.calendar_parser import normalize_calendar_text


# ==========================================================
# Google Calendar
# ==========================================================

def get_calendar_service():
    """Return an authenticated Google Calendar service."""

    credentials = get_google_credentials()

    return build(
        "calendar",
        "v3",
        credentials=credentials,
        cache_discovery=False,
    )


# ==========================================================
# Event Creation
# ==========================================================

def create_calendar_event(
    *,
    title: str,
    start_time=None,
    end_time=None,
    start_date=None,
    end_date=None,
    all_day: bool = False,
):
    """
    Create a timed or all-day Google Calendar event.

    For all-day events, end_date is inclusive inside ShaunMariaOS.
    Google Calendar requires an exclusive end date, so one day is added.
    """

    if not title.strip():
        raise ValueError(
            "The calendar event needs a title."
        )

    service = get_calendar_service()

    if all_day:
        if start_date is None or end_date is None:
            raise ValueError(
                "All-day events require start and end dates."
            )

        if end_date < start_date:
            raise ValueError(
                "The event end date cannot be before its start date."
            )

        event_body = {
            "summary": title.strip(),
            "start": {
                "date": start_date.isoformat(),
            },
            "end": {
                "date": (
                    end_date
                    + timedelta(days=1)
                ).isoformat(),
            },
        }

    else:
        if start_time is None or end_time is None:
            raise ValueError(
                "Timed events require start and end times."
            )

        if end_time <= start_time:
            raise ValueError(
                "The event end time must be after its start time."
            )

        event_body = {
            "summary": title.strip(),
            "start": {
                "dateTime": start_time.isoformat(),
                "timeZone": "Asia/Singapore",
            },
            "end": {
                "dateTime": end_time.isoformat(),
                "timeZone": "Asia/Singapore",
            },
        }

    return (
        service.events()
        .insert(
            calendarId=GOOGLE_CALENDAR_ID,
            body=event_body,
        )
        .execute()
    )

# ==========================================================
# Natural Language Parsing
# ==========================================================

# ==========================================================
# Existing Dashboard Functions
# ==========================================================
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

        return event_time.strftime("%I:%M %p").lstrip("0")

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

def get_events_for_date(target_date):
    """Return calendar events for one specific date."""

    service = get_calendar_service()

    start_of_day = datetime.combine(
        target_date,
        datetime.min.time(),
    )

    end_of_day = start_of_day + timedelta(days=1)

    result = (
        service.events()
        .list(
            calendarId=GOOGLE_CALENDAR_ID,
            timeMin=start_of_day.isoformat() + "+08:00",
            timeMax=end_of_day.isoformat() + "+08:00",
            singleEvents=True,
            orderBy="startTime",
        )
        .execute()
    )

    return result.get("items", [])


def get_next_calendar_event():
    """Return the next upcoming calendar event."""

    service = get_calendar_service()

    now = datetime.now().astimezone()

    result = (
        service.events()
        .list(
            calendarId=GOOGLE_CALENDAR_ID,
            timeMin=now.isoformat(),
            maxResults=1,
            singleEvents=True,
            orderBy="startTime",
        )
        .execute()
    )

    events = result.get("items", [])

    if not events:
        return None

    return events[0]

def resolve_calendar_query_date(text: str):
    """Resolve today, tomorrow, or weekday queries."""

    normalized = normalize_calendar_text(text)
    today = datetime.now().date()

    if "today" in normalized:
        return today

    if "tomorrow" in normalized:
        return today + timedelta(days=1)

    weekdays = {
        "monday": 0,
        "tuesday": 1,
        "wednesday": 2,
        "thursday": 3,
        "friday": 4,
        "saturday": 5,
        "sunday": 6,
    }

    for weekday_name, weekday_number in weekdays.items():
        if weekday_name in normalized:
            days_ahead = (
                weekday_number - today.weekday()
            ) % 7

            if days_ahead == 0:
                days_ahead = 7

            return today + timedelta(days=days_ahead)

    return None

def format_calendar_event(event: dict) -> str:
    """Format one Google Calendar event for Telegram."""

    title = event.get("summary", "Untitled Event")

    start_data = event.get("start", {})
    start_value = (
        start_data.get("dateTime")
        or start_data.get("date")
    )

    if not start_value:
        return f"• {title}"

    if "T" not in start_value:
        return f"• All day — {title}"

    start_time = datetime.fromisoformat(
        start_value.replace("Z", "+00:00")
    )

    time_label = start_time.strftime(
        "%I:%M %p"
    ).lstrip("0")

    return f"• {time_label} — {title}"

# ==========================================================
# Event Search and Deletion
# ==========================================================

def search_upcoming_calendar_events(
    search_text: str,
    *,
    max_results: int = 10,
) -> list[dict]:
    """
    Search upcoming Calendar events by title.

    Results are limited to approximately the next year.
    """

    query = search_text.strip()

    if not query:
        return []

    service = get_calendar_service()
    now = sg_now()
    search_end = now + timedelta(days=365)

    result = (
        service.events()
        .list(
            calendarId=GOOGLE_CALENDAR_ID,
            timeMin=now.isoformat(),
            timeMax=search_end.isoformat(),
            q=query,
            singleEvents=True,
            orderBy="startTime",
            maxResults=max_results,
        )
        .execute()
    )

    events = result.get("items", [])
    normalized_query = query.casefold()

    return [
        event
        for event in events
        if normalized_query
        in event.get(
            "summary",
            "",
        ).casefold()
    ]


def delete_calendar_event(
    event_id: str,
) -> None:
    """Delete one Google Calendar event."""

    if not event_id.strip():
        raise ValueError(
            "A Calendar event ID is required."
        )

    service = get_calendar_service()

    (
        service.events()
        .delete(
            calendarId=GOOGLE_CALENDAR_ID,
            eventId=event_id,
        )
        .execute()
    )


def get_event_date_label(
    event: dict,
) -> str:
    """Return a readable event date and time."""

    start_data = event.get("start", {})
    date_time_text = start_data.get("dateTime")
    date_text = start_data.get("date")

    if date_time_text:
        event_time = datetime.fromisoformat(
            date_time_text.replace(
                "Z",
                "+00:00",
            )
        ).astimezone(SINGAPORE_TZ)

        return event_time.strftime(
            "%d %B %Y, %I:%M %p"
        ).replace(
            " 0",
            " ",
        )

    if date_text:
        event_date = datetime.fromisoformat(
            date_text
        ).date()

        return (
            event_date.strftime(
                "%d %B %Y"
            )
            + " — All day"
        )

    return "Date unavailable"

# ==========================================================
# Event Updates
# ==========================================================

def get_calendar_event(
    event_id: str,
) -> dict:
    """Return one Google Calendar event."""

    if not event_id.strip():
        raise ValueError(
            "A Calendar event ID is required."
        )

    service = get_calendar_service()

    return (
        service.events()
        .get(
            calendarId=GOOGLE_CALENDAR_ID,
            eventId=event_id,
        )
        .execute()
    )


def update_calendar_event(
    event_id: str,
    event_updates: dict,
) -> dict:
    """
    Patch an existing Google Calendar event.

    Only fields supplied in event_updates are changed.
    """

    if not event_id.strip():
        raise ValueError(
            "A Calendar event ID is required."
        )

    if not event_updates:
        raise ValueError(
            "Calendar update data is missing."
        )

    service = get_calendar_service()

    return (
        service.events()
        .patch(
            calendarId=GOOGLE_CALENDAR_ID,
            eventId=event_id,
            body=event_updates,
        )
        .execute()
    )