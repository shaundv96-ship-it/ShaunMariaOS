"""
ShaunMariaOS

Calendar Parser
Parses timed, all-day, and multi-day calendar events.
"""

import re
from datetime import date, datetime, time, timedelta

from utils.time import SINGAPORE_TZ, sg_now


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

ALL_DAY_KEYWORDS = {
    "trip",
    "leave",
    "annual leave",
    "holiday",
    "vacation",
    "birthday",
    "retreat",
    "camp",
    "staycation",
    "off day",
    "office closed",
}

SMALL_TITLE_WORDS = {
    "a",
    "an",
    "and",
    "at",
    "for",
    "from",
    "in",
    "of",
    "on",
    "the",
    "to",
    "with",
}


# ==========================================================
# Normalisation
# ==========================================================

def normalize_calendar_text(text: str) -> str:
    """
    Normalise calendar shorthand and ordinal dates.

    Examples:
        tmrw -> tomorrow
        fri -> friday
        sept -> september
        3rd -> 3
    """

    normalized = text.strip().casefold()

    normalized = re.sub(
        r"\b(\d{1,2})(st|nd|rd|th)\b",
        r"\1",
        normalized,
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

    replacement_pattern = re.compile(
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
        re.IGNORECASE,
    )

    normalized = replacement_pattern.sub(
        lambda match: replacements[
            match.group(0).casefold()
        ],
        normalized,
    )

    return re.sub(
        r"\s+",
        " ",
        normalized,
    ).strip()


# ==========================================================
# Shared Date Helpers
# ==========================================================

def next_weekday(
    weekday_number: int,
    *,
    reference_date: date | None = None,
    force_next_week: bool = False,
) -> date:
    """Return the next occurrence of a weekday."""

    reference = reference_date or sg_now().date()

    days_ahead = (
        weekday_number - reference.weekday()
    ) % 7

    if days_ahead == 0:
        days_ahead = 7

    if force_next_week:
        days_ahead += 7

    return reference + timedelta(
        days=days_ahead,
    )


def build_month_date(
    day: int,
    month: int,
    year: int | None = None,
) -> date | None:
    """Build a valid future-facing calendar date."""

    today = sg_now().date()
    selected_year = year or today.year

    try:
        result = date(
            selected_year,
            month,
            day,
        )
    except ValueError:
        return None

    if year is None and result < today:
        try:
            result = result.replace(
                year=selected_year + 1,
            )
        except ValueError:
            return None

    return result


# ==========================================================
# Time Parsing
# ==========================================================

def parse_calendar_time(
    text: str,
) -> time | None:
    """Parse common 12-hour and 24-hour time formats."""

    twelve_hour_match = re.search(
        r"\b(?:at\s+)?"
        r"(\d{1,2})"
        r"(?:[:.](\d{2}))?"
        r"\s*(am|pm)\b",
        text,
        re.IGNORECASE,
    )

    if twelve_hour_match:
        hour = int(
            twelve_hour_match.group(1)
        )

        minute = int(
            twelve_hour_match.group(2)
            or 0
        )

        meridiem = (
            twelve_hour_match.group(3)
            .casefold()
        )

        if hour < 1 or hour > 12:
            return None

        if minute > 59:
            return None

        if meridiem == "pm" and hour != 12:
            hour += 12

        if meridiem == "am" and hour == 12:
            hour = 0

        return time(
            hour=hour,
            minute=minute,
        )

    twenty_four_hour_match = re.search(
        r"\b([01]?\d|2[0-3]):([0-5]\d)\b",
        text,
    )

    if twenty_four_hour_match:
        return time(
            hour=int(
                twenty_four_hour_match.group(1)
            ),
            minute=int(
                twenty_four_hour_match.group(2)
            ),
        )

    return None


# ==========================================================
# Single Date Parsing
# ==========================================================

def parse_calendar_date(
    text: str,
) -> date | None:
    """Parse one calendar date."""

    normalized = normalize_calendar_text(text)
    today = sg_now().date()

    if re.search(
        r"\btoday\b",
        normalized,
    ):
        return today

    if re.search(
        r"\btomorrow\b",
        normalized,
    ):
        return today + timedelta(days=1)

    weekday_match = re.search(
        r"\b(next\s+)?"
        r"(monday|tuesday|wednesday|thursday|"
        r"friday|saturday|sunday)\b",
        normalized,
    )

    if weekday_match:
        return next_weekday(
            WEEKDAYS[
                weekday_match.group(2)
            ],
            force_next_week=bool(
                weekday_match.group(1)
            ),
        )

    month_match = re.search(
        r"\b(\d{1,2})\s+"
        r"(january|february|march|april|may|"
        r"june|july|august|september|october|"
        r"november|december)"
        r"(?:\s+(\d{4}))?\b",
        normalized,
    )

    if month_match:
        return build_month_date(
            day=int(month_match.group(1)),
            month=MONTHS[
                month_match.group(2)
            ],
            year=(
                int(month_match.group(3))
                if month_match.group(3)
                else None
            ),
        )

    return None


# ==========================================================
# Date-Range Parsing
# ==========================================================

def parse_relative_date_range(
    text: str,
) -> tuple[date, date] | None:
    """
    Parse this weekend, next weekend, or next week.

    Returned end date is inclusive.
    """

    normalized = normalize_calendar_text(text)
    today = sg_now().date()

    if "this weekend" in normalized:
        days_until_saturday = (
            WEEKDAYS["saturday"]
            - today.weekday()
        ) % 7

        start_date = (
            today
            + timedelta(
                days=days_until_saturday,
            )
        )

        return (
            start_date,
            start_date + timedelta(days=1),
        )

    if "next weekend" in normalized:
        days_until_saturday = (
            WEEKDAYS["saturday"]
            - today.weekday()
        ) % 7

        start_date = (
            today
            + timedelta(
                days=days_until_saturday + 7,
            )
        )

        return (
            start_date,
            start_date + timedelta(days=1),
        )

    if "next week" in normalized:
        days_until_monday = (
            WEEKDAYS["monday"]
            - today.weekday()
        ) % 7

        if days_until_monday == 0:
            days_until_monday = 7

        start_date = (
            today
            + timedelta(
                days=days_until_monday,
            )
        )

        return (
            start_date,
            start_date + timedelta(days=6),
        )

    return None


def parse_weekday_date_range(
    text: str,
) -> tuple[date, date] | None:
    """
    Parse weekday ranges.

    Examples:
        Saturday to Sunday
        Fri-Sun
        next Monday to Wednesday
    """

    normalized = normalize_calendar_text(text)

    match = re.search(
        r"\b(next\s+)?"
        r"(monday|tuesday|wednesday|thursday|"
        r"friday|saturday|sunday)"
        r"\s*(?:to|until|through|-)\s*"
        r"(next\s+)?"
        r"(monday|tuesday|wednesday|thursday|"
        r"friday|saturday|sunday)\b",
        normalized,
    )

    if not match:
        return None

    start_date = next_weekday(
        WEEKDAYS[match.group(2)],
        force_next_week=bool(
            match.group(1)
        ),
    )

    end_weekday = WEEKDAYS[
        match.group(4)
    ]

    days_to_end = (
        end_weekday
        - start_date.weekday()
    ) % 7

    if days_to_end == 0:
        days_to_end = 7

    if match.group(3):
        days_to_end += 7

    end_date = (
        start_date
        + timedelta(days=days_to_end)
    )

    return start_date, end_date


def parse_numbered_date_range(
    text: str,
) -> tuple[date, date] | None:
    """
    Parse numbered month ranges.

    Examples:
        3-5 Aug
        3 Aug to 5 Aug
        30 Aug to 2 Sept
        12 Sept to 15 Sept 2026
    """

    normalized = normalize_calendar_text(text)

    # Both dates include their own month.
    full_range_match = re.search(
        r"\b(\d{1,2})\s+"
        r"(january|february|march|april|may|"
        r"june|july|august|september|october|"
        r"november|december)"
        r"(?:\s+(\d{4}))?"
        r"\s*(?:to|until|through|-)\s*"
        r"(\d{1,2})\s+"
        r"(january|february|march|april|may|"
        r"june|july|august|september|october|"
        r"november|december)"
        r"(?:\s+(\d{4}))?\b",
        normalized,
    )

    if full_range_match:
        start_year = (
            int(full_range_match.group(3))
            if full_range_match.group(3)
            else None
        )

        end_year = (
            int(full_range_match.group(6))
            if full_range_match.group(6)
            else start_year
        )

        start_date = build_month_date(
            day=int(
                full_range_match.group(1)
            ),
            month=MONTHS[
                full_range_match.group(2)
            ],
            year=start_year,
        )

        end_date = build_month_date(
            day=int(
                full_range_match.group(4)
            ),
            month=MONTHS[
                full_range_match.group(5)
            ],
            year=end_year,
        )

        if not start_date or not end_date:
            return None

        if end_date < start_date:
            try:
                end_date = end_date.replace(
                    year=end_date.year + 1,
                )
            except ValueError:
                return None

        return start_date, end_date

    # One shared month: 3-5 Aug.
    shared_month_match = re.search(
        r"\b(\d{1,2})"
        r"\s*(?:to|until|through|-)\s*"
        r"(\d{1,2})\s+"
        r"(january|february|march|april|may|"
        r"june|july|august|september|october|"
        r"november|december)"
        r"(?:\s+(\d{4}))?\b",
        normalized,
    )

    if not shared_month_match:
        return None

    year = (
        int(shared_month_match.group(4))
        if shared_month_match.group(4)
        else None
    )

    month = MONTHS[
        shared_month_match.group(3)
    ]

    start_date = build_month_date(
        day=int(
            shared_month_match.group(1)
        ),
        month=month,
        year=year,
    )

    end_date = build_month_date(
        day=int(
            shared_month_match.group(2)
        ),
        month=month,
        year=(
            start_date.year
            if start_date
            else year
        ),
    )

    if (
        not start_date
        or not end_date
        or end_date < start_date
    ):
        return None

    return start_date, end_date


def parse_date_range(
    text: str,
) -> tuple[date, date] | None:
    """Parse any supported date-range format."""

    return (
        parse_relative_date_range(text)
        or parse_numbered_date_range(text)
        or parse_weekday_date_range(text)
    )


# ==========================================================
# Title Cleaning
# ==========================================================

def smart_title_case(text: str) -> str:
    """Apply readable title casing while preserving small words."""

    words = text.split()

    if not words:
        return "Untitled Event"

    result = []

    for index, word in enumerate(words):
        if (
            index > 0
            and word.casefold()
            in SMALL_TITLE_WORDS
        ):
            result.append(
                word.casefold()
            )
        else:
            result.append(
                word[:1].upper()
                + word[1:]
            )

    return " ".join(result)


def clean_calendar_title(
    text: str,
) -> str:
    """Remove parsed date and time phrases from an event title."""

    title = normalize_calendar_text(text)

    patterns = (
        r"\b(?:this|next)\s+weekend\b",
        r"\bnext\s+week\b",
        (
            r"\b(?:next\s+)?"
            r"(?:monday|tuesday|wednesday|thursday|"
            r"friday|saturday|sunday)"
            r"\s*(?:to|until|through|-)\s*"
            r"(?:next\s+)?"
            r"(?:monday|tuesday|wednesday|thursday|"
            r"friday|saturday|sunday)\b"
        ),
        (
            r"\b\d{1,2}\s+"
            r"(?:january|february|march|april|may|"
            r"june|july|august|september|october|"
            r"november|december)"
            r"(?:\s+\d{4})?"
            r"\s*(?:to|until|through|-)\s*"
            r"\d{1,2}\s+"
            r"(?:january|february|march|april|may|"
            r"june|july|august|september|october|"
            r"november|december)"
            r"(?:\s+\d{4})?\b"
        ),
        (
            r"\b\d{1,2}"
            r"\s*(?:to|until|through|-)\s*"
            r"\d{1,2}\s+"
            r"(?:january|february|march|april|may|"
            r"june|july|august|september|october|"
            r"november|december)"
            r"(?:\s+\d{4})?\b"
        ),
        r"\b(?:today|tomorrow)\b",
        (
            r"\bnext\s+"
            r"(?:monday|tuesday|wednesday|thursday|"
            r"friday|saturday|sunday)\b"
        ),
        (
            r"\b(?:monday|tuesday|wednesday|thursday|"
            r"friday|saturday|sunday)\b"
        ),
        (
            r"\b\d{1,2}\s+"
            r"(?:january|february|march|april|may|"
            r"june|july|august|september|october|"
            r"november|december)"
            r"(?:\s+\d{4})?\b"
        ),
        (
            r"\b(?:at\s+)?"
            r"\d{1,2}(?:[:.]\d{2})?"
            r"\s*(?:am|pm)\b"
        ),
        r"\b(?:[01]?\d|2[0-3]):[0-5]\d\b",
    )

    for pattern in patterns:
        title = re.sub(
            pattern,
            " ",
            title,
            flags=re.IGNORECASE,
        )

    title = re.sub(
        r"\s+",
        " ",
        title,
    ).strip(" ,.-")

    return smart_title_case(title)


# ==========================================================
# Event Parsing
# ==========================================================

def looks_like_all_day_event(
    text: str,
) -> bool:
    """Return whether the message naturally suggests an all-day event."""

    normalized = normalize_calendar_text(text)

    return any(
        keyword in normalized
        for keyword in ALL_DAY_KEYWORDS
    )


def parse_calendar_event(
    text: str,
) -> dict | None:
    """
    Parse a timed, all-day, or multi-day calendar event.

    Multi-day events take priority over timed events.
    """

    normalized = normalize_calendar_text(text)
    title = clean_calendar_title(normalized)

    date_range = parse_date_range(
        normalized
    )

    if date_range:
        start_date, end_date = date_range

        return {
            "title": title,
            "all_day": True,
            "start_date": start_date,
            "end_date": end_date,
        }

    event_date = parse_calendar_date(
        normalized
    )

    event_time = parse_calendar_time(
        normalized
    )

    if event_date and event_time:
        start_time = datetime.combine(
            event_date,
            event_time,
            tzinfo=SINGAPORE_TZ,
        )

        return {
            "title": title,
            "all_day": False,
            "start_time": start_time,
            "end_time": (
                start_time
                + timedelta(hours=1)
            ),
        }

    if (
        event_date
        and event_time is None
        and looks_like_all_day_event(normalized)
    ):
        return {
            "title": title,
            "all_day": True,
            "start_date": event_date,
            "end_date": event_date,
        }

    return None