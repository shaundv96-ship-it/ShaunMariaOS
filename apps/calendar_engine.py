"""
ShaunMariaOS

Calendar Engine
"""

import re
from datetime import date, datetime, time, timedelta

from googleapiclient.discovery import build

from apps.google_engine import get_google_credentials
from config import GOOGLE_CALENDAR_ID
from utils.time import SINGAPORE_TZ, sg_now
from apps.calendar_parser import (
    normalize_calendar_text,
    parse_calendar_event,
)


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

WEEKDAYS = {
    "monday": 0,
    "tuesday": 1,
    "wednesday": 2,
    "thursday": 3,
    "friday": 4,
    "saturday": 5,
    "sunday": 6,
}

MONTHS = {
    "january": 1,
    "february": 2,
    "march": 3,
    "april": 4,
    "may": 5,
    "june": 6,
    "july": 7,
    "august": 8,
    "september": 9,
    "october": 10,
    "november": 11,
    "december": 12,
}


def parse_calendar_time(text: str):
    """Parse a calendar time from natural-language text."""

    # 12-hour format:
    # 7pm, 7 pm, 7:30pm, at 7pm
    match = re.search(
        r"\b(?:at\s+)?(\d{1,2})(?:[:.](\d{2}))?\s*(am|pm)\b",
        text,
        re.IGNORECASE,
    )

    if match:
        hour = int(match.group(1))
        minute = int(match.group(2) or 0)
        ampm = match.group(3).lower()

        if hour < 1 or hour > 12:
            return None

        if minute > 59:
            return None

        if ampm == "pm" and hour != 12:
            hour += 12

        if ampm == "am" and hour == 12:
            hour = 0

        return time(
            hour=hour,
            minute=minute,
        )

    # 24-hour format:
    # 19:00, 08:30
    match = re.search(
        r"\b([01]?\d|2[0-3]):([0-5]\d)\b",
        text,
        re.IGNORECASE,
    )

    if match:
        return time(
            hour=int(match.group(1)),
            minute=int(match.group(2)),
        )

    return None

def parse_calendar_date(text: str):

    today = sg_now().date()
    lowered = text.lower()

    if "today" in lowered:
        return today

    if "tomorrow" in lowered:
        return today + timedelta(days=1)

    weekday_match = re.search(
        r"(next\s+)?(monday|tuesday|wednesday|thursday|friday|saturday|sunday)",
        lowered,
    )

    if weekday_match:

        weekday = WEEKDAYS[weekday_match.group(2)]

        delta = (weekday - today.weekday()) % 7

        if delta == 0:
            delta = 7

        if weekday_match.group(1):
            delta += 7

        return today + timedelta(days=delta)

    month_pattern = (
        r"(\d{1,2})\s+"
        r"(january|february|march|april|may|june|"
        r"july|august|september|october|november|december)"
        r"(?:\s+(\d{4}))?"
    )

    month_match = re.search(
        month_pattern,
        lowered,
    )

    if month_match:

        day = int(month_match.group(1))
        month = MONTHS[month_match.group(2)]
        year = int(month_match.group(3) or today.year)

        date = datetime(
            year,
            month,
            day,
        ).date()

        if not month_match.group(3):

            if date < today:
                date = date.replace(
                    year=year + 1,
                )

        return date

    return None


def clean_calendar_title(text: str):

    title = text

    patterns = [

        r"\btoday\b",
        r"\btomorrow\b",

        r"\bnext\s+(?:monday|tuesday|wednesday|thursday|friday|saturday|sunday)\b",

        r"\b(?:monday|tuesday|wednesday|thursday|friday|saturday|sunday)\b",

        r"\d{1,2}\s+(?:january|february|march|april|may|june|july|august|september|october|november|december)(?:\s+\d{4})?",

        r"\bat\s+\d{1,2}(?::\d{2})?\s*(?:am|pm)?",

        r"\d{1,2}(?::\d{2})?\s*(?:am|pm)",
    ]

    for pattern in patterns:

        title = re.sub(
            pattern,
            "",
            title,
            flags=re.IGNORECASE,
        )

    title = re.sub(
        r"\s+",
        " ",
        title,
    ).strip(" ,.-")

    if not title:
        return "Untitled Event"

    return title[0].upper() + title[1:]


def parse_calendar_event(text: str):
    normalized_text = normalize_calendar_text(text)

    event_date = parse_calendar_date(normalized_text)
    event_time = parse_calendar_time(normalized_text)

    if event_date is None or event_time is None:
        return None

    title = clean_calendar_title(normalized_text)

    start_time = datetime.combine(
        event_date,
        event_time,
    )

    end_time = start_time + timedelta(hours=1)

    return {
        "title": title,
        "start_time": start_time,
        "end_time": end_time,
    }

def normalize_calendar_text(text: str) -> str:
    """
    Normalise common calendar shorthand and ordinal dates.

    Examples:
    tmrw -> tomorrow
    fri -> friday
    sept -> september
    3rd -> 3
    """

    normalized = text.lower().strip()

    # Convert ordinal dates:
    # 1st, 2nd, 3rd, 4th -> 1, 2, 3, 4
    normalized = re.sub(
        r"\b(\d{1,2})(st|nd|rd|th)\b",
        r"\1",
        normalized,
        flags=re.IGNORECASE,
    )

    replacements = {
        # Relative dates
        "tdy": "today",
        "tmr": "tomorrow",
        "tmrw": "tomorrow",
        "2moro": "tomorrow",

        # Weekdays
        "mon": "monday",
        "tue": "tuesday",
        "tues": "tuesday",
        "wed": "wednesday",
        "thu": "thursday",
        "thur": "thursday",
        "thurs": "thursday",
        "fri": "friday",
        "sat": "saturday",
        "sun": "sunday",

        # Months
        "jan": "january",
        "feb": "february",
        "mar": "march",
        "apr": "april",
        "jun": "june",
        "jul": "july",
        "aug": "august",
        "sep": "september",
        "sept": "september",
        "oct": "october",
        "nov": "november",
        "dec": "december",
    }

    pattern = re.compile(
        r"\b("
        + "|".join(
            re.escape(key)
            for key in sorted(
                replacements,
                key=len,
                reverse=True,
            )
        )
        + r")\b",
        flags=re.IGNORECASE,
    )

    normalized = pattern.sub(
        lambda match: replacements[match.group(0).lower()],
        normalized,
    )

    return re.sub(r"\s+", " ", normalized).strip()
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