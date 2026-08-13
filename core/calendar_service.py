"""
ShaunMariaOS

Calendar Service
Reusable CalendarOS business logic for Telegram, web, and future app clients.
"""

from dataclasses import dataclass
from typing import Any

from apps.calendar_engine import (
    create_calendar_event,
    get_calendar_events_for_date,
    get_events_for_month,
)

from apps.calendar_parser import parse_calendar_event


@dataclass
class CalendarCreationResult:
    """Structured result returned after parsing and creating an event."""

    success: bool
    status: str
    message: str
    parsed_event: dict[str, Any] | None = None
    created_event: dict[str, Any] | None = None


def create_event_from_text(
    text: str,
) -> CalendarCreationResult:
    """
    Parse natural language and create a Google Calendar event.

    This function contains no Telegram-specific formatting or replies.
    It can be reused by Telegram, an API, or the future app.
    """

    parsed_event = parse_calendar_event(
        text
    )

    if parsed_event is None:
        return CalendarCreationResult(
            success=False,
            status="invalid_input",
            message=(
                "Please include a date, or a date and time."
            ),
        )

    if parsed_event.get("incomplete"):
        return CalendarCreationResult(
            success=False,
            status=parsed_event.get(
                "reason",
                "incomplete_input",
            ),
            message=(
                "This recurring event needs more information."
            ),
            parsed_event=parsed_event,
        )

    title = parsed_event["title"]
    all_day = parsed_event["all_day"]
    recurrence = parsed_event.get(
        "recurrence"
    )

    if all_day:
        created_event = create_calendar_event(
            title=title,
            start_date=parsed_event["start_date"],
            end_date=parsed_event["end_date"],
            all_day=True,
            recurrence=recurrence,
        )

    else:
        created_event = create_calendar_event(
            title=title,
            start_time=parsed_event["start_time"],
            end_time=parsed_event["end_time"],
            all_day=False,
            recurrence=recurrence,
        )

    return CalendarCreationResult(
        success=True,
        status="created",
        message="Calendar event created.",
        parsed_event=parsed_event,
        created_event=created_event,
    )

@dataclass
class CalendarTodayResult:
    """Result returned when loading today's calendar."""

    success: bool
    status: str
    message: str
    events: list[dict]

def normalize_calendar_event(
    event: dict,
) -> dict:
    """Convert a Google Calendar event into CalendarOS format."""

    start = event.get(
        "start",
        {},
    )

    end = event.get(
        "end",
        {},
    )

    all_day = "date" in start

    return {
        "id": event.get("id"),
        "title": event.get(
            "summary",
            "Untitled Event",
        ),
        "all_day": all_day,
        "start": (
            start.get("date")
            if all_day
            else start.get("dateTime")
        ),
        "end": (
            end.get("date")
            if all_day
            else end.get("dateTime")
        ),
        "calendar_link": event.get(
            "htmlLink"
        ),
    }

@dataclass
class CalendarMonthResult:
    """Result returned when loading one calendar month."""

    success: bool
    status: str
    message: str
    year: int
    month: int
    events: list[dict]

def get_month_events(
    year: int,
    month: int,
) -> CalendarMonthResult:
    """Load all events for one calendar month."""

    if month < 1 or month > 12:
        return CalendarMonthResult(
            success=False,
            status="invalid_month",
            message="Month must be between 1 and 12.",
            year=year,
            month=month,
            events=[],
        )

    try:
        raw_events = get_events_for_month(
            year,
            month,
        )

        events = [
            normalize_calendar_event(event)
            for event in raw_events
        ]

        return CalendarMonthResult(
            success=True,
            status="ok",
            message="Calendar month loaded.",
            year=year,
            month=month,
            events=events,
        )

    except Exception as exc:
        return CalendarMonthResult(
            success=False,
            status="error",
            message=str(exc),
            year=year,
            month=month,
            events=[],
        )

def get_today_events() -> CalendarTodayResult:
    """
    Load today's events from the shared Google Calendar.

    Returns clean, client-independent event data for
    Telegram, APIs, and the ShaunMariaOS app.
    """

    from apps.calendar_engine import (
        get_calendar_events_for_date,
    )
    from utils.time import sg_now

    try:
        today = sg_now().date()

        raw_events = get_calendar_events_for_date(
            today
        )

        events = [
            normalize_calendar_event(event)
            for event in raw_events
        ]

        for event in raw_events:
            start = event.get(
                "start",
                {},
            )

            end = event.get(
                "end",
                {},
            )

            all_day = "date" in start

            events.append(
                {
                    "id": event.get("id"),
                    "title": event.get(
                        "summary",
                        "Untitled Event",
                    ),
                    "all_day": all_day,
                    "start": (
                        start.get("date")
                        if all_day
                        else start.get("dateTime")
                    ),
                    "end": (
                        end.get("date")
                        if all_day
                        else end.get("dateTime")
                    ),
                    "calendar_link": event.get(
                        "htmlLink"
                    ),
                }
            )

        return CalendarTodayResult(
            success=True,
            status="ok",
            message="Today's calendar loaded.",
            events=events,
        )

    except Exception as exc:
        return CalendarTodayResult(
            success=False,
            status="error",
            message=str(exc),
            events=[],
        )

def get_events_for_date(
    target_date,
) -> CalendarTodayResult:
    """
    Load events for a specific date.

    Returns the same clean event structure used by
    the ShaunMariaOS web app.
    """

    from apps.calendar_engine import (
        get_calendar_events_for_date,
    )

    try:
        raw_events = get_calendar_events_for_date(
            target_date
        )

        events = [
            normalize_calendar_event(event)
            for event in raw_events
        ]

        for event in raw_events:
            start = event.get(
                "start",
                {},
            )

            end = event.get(
                "end",
                {},
            )

            all_day = "date" in start

            events.append(
                {
                    "id": event.get("id"),
                    "title": event.get(
                        "summary",
                        "Untitled Event",
                    ),
                    "all_day": all_day,
                    "start": (
                        start.get("date")
                        if all_day
                        else start.get("dateTime")
                    ),
                    "end": (
                        end.get("date")
                        if all_day
                        else end.get("dateTime")
                    ),
                    "calendar_link": event.get(
                        "htmlLink"
                    ),
                }
            )

        return CalendarTodayResult(
            success=True,
            status="ok",
            message="Calendar loaded.",
            events=events,
        )

    except Exception as exc:
        return CalendarTodayResult(
            success=False,
            status="error",
            message=str(exc),
            events=[],
        )