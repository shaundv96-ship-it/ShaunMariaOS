"""
ShaunMariaOS

Calendar Parser
Parses timed, all-day, multi-day, and recurring events.
"""

import re
from datetime import date, datetime, time, timedelta

from apps.calendar_recurrence import parse_recurrence
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

ACRONYMS = {
    "ai": "AI",
    "api": "API",
    "bto": "BTO",
    "cpf": "CPF",
    "hdb": "HDB",
    "hr": "HR",
    "jb": "JB",
    "kl": "KL",
    "sg": "SG",
    "uk": "UK",
    "usa": "USA",
}

ALL_DAY_KEYWORDS = {
    "annual leave",
    "birthday",
    "camp",
    "holiday",
    "leave",
    "off day",
    "office closed",
    "retreat",
    "staycation",
    "trip",
    "vacation",
}


# ==========================================================
# Normalisation
# ==========================================================

def normalize_calendar_text(
    text: str,
) -> str:
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
        "tdy": "today",
        "tmr": "tomorrow",
        "tmrw": "tomorrow",
        "2moro": "tomorrow",

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
# Date Helpers
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
        weekday_number
        - reference.weekday()
    ) % 7

    if days_ahead == 0:
        days_ahead = 7

    if force_next_week:
        days_ahead += 7

    return (
        reference
        + timedelta(days=days_ahead)
    )


def build_month_date(
    day: int,
    month: int,
    year: int | None = None,
) -> date | None:
    """Build a valid future-facing date."""

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

    if (
        year is None
        and result < today
    ):
        try:
            result = result.replace(
                year=result.year + 1,
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
    """
    Parse common time formats.

    Supported:
        7pm
        7:30pm
        7.30pm
        730pm
        815am
        19:00
    """

    twelve_hour_match = re.search(
        r"\b(?:at\s+)?"
        r"(\d{1,4})"
        r"(?:[:.](\d{2}))?"
        r"\s*(am|pm)\b",
        text,
        re.IGNORECASE,
    )

    if twelve_hour_match:
        raw_value = twelve_hour_match.group(1)
        explicit_minutes = twelve_hour_match.group(2)

        if explicit_minutes is not None:
            hour = int(raw_value)
            minute = int(explicit_minutes)

        elif len(raw_value) <= 2:
            hour = int(raw_value)
            minute = 0

        elif len(raw_value) in {3, 4}:
            hour = int(raw_value[:-2])
            minute = int(raw_value[-2:])

        else:
            return None

        meridiem = (
            twelve_hour_match.group(3)
            .casefold()
        )

        if not 1 <= hour <= 12:
            return None

        if not 0 <= minute <= 59:
            return None

        if (
            meridiem == "pm"
            and hour != 12
        ):
            hour += 12

        if (
            meridiem == "am"
            and hour == 12
        ):
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

    normalized = normalize_calendar_text(
        text
    )

    today = sg_now().date()

    # ======================================================
    # Relative dates
    # ======================================================

    if re.search(
        r"\btoday\b",
        normalized,
    ):
        return today

    if re.search(
        r"\btomorrow\b",
        normalized,
    ):
        return (
            today
            + timedelta(days=1)
        )

    # ======================================================
    # Weekdays
    # ======================================================

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

    # ======================================================
    # Month-first dates
    #
    # October 5
    # October 5 2026
    # ======================================================

    month_first_match = re.search(
        r"\b"
        r"(january|february|march|april|may|"
        r"june|july|august|september|october|"
        r"november|december)"
        r"\s+(\d{1,2})"
        r"(?:\s+(\d{4}))?\b",
        normalized,
    )

    if month_first_match:
        return build_month_date(
            day=int(
                month_first_match.group(2)
            ),
            month=MONTHS[
                month_first_match.group(1)
            ],
            year=(
                int(
                    month_first_match.group(3)
                )
                if month_first_match.group(3)
                else None
            ),
        )

    # ======================================================
    # Day-first dates
    #
    # 5 October
    # 5 October 2026
    # ======================================================

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
            day=int(
                month_match.group(1)
            ),
            month=MONTHS[
                month_match.group(2)
            ],
            year=(
                int(
                    month_match.group(3)
                )
                if month_match.group(3)
                else None
            ),
        )

    return None

# ==========================================================
# Date Range Parsing
# ==========================================================

def parse_relative_date_range(
    text: str,
) -> tuple[date, date] | None:
    """Parse this weekend, next weekend, or next week."""

    normalized = normalize_calendar_text(
        text
    )

    today = sg_now().date()

    if "this weekend" in normalized:
        days_until_saturday = (
            5 - today.weekday()
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
            5 - today.weekday()
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
            0 - today.weekday()
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
    """Parse ranges such as Friday to Sunday."""

    normalized = normalize_calendar_text(
        text
    )

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
        WEEKDAYS[
            match.group(2)
        ],
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

    return (
        start_date,
        start_date + timedelta(
            days=days_to_end,
        ),
    )


def parse_numbered_date_range(
    text: str,
) -> tuple[date, date] | None:
    """
    Parse numbered date ranges.

    Supported examples:
        3-5 Aug
        3 Aug to 5 Aug
        30 Aug to 2 Sept

        Aug 3-5
        Aug 3 to 5
        Aug 30 to Sept 2
        Oct 9 to 11 JB Trip
        JB Trip Oct 9-11
    """

    normalized = normalize_calendar_text(
        text
    )

    month_pattern = (
        r"(january|february|march|april|may|"
        r"june|july|august|september|october|"
        r"november|december)"
    )


    # ======================================================
    # Month-first, different months
    #
    # October 30 to November 2
    # ======================================================

    month_first_full_match = re.search(
        rf"\b{month_pattern}\s+"
        r"(\d{1,2})"
        r"(?:\s+(\d{4}))?"
        r"\s*(?:to|until|through|-)\s*"
        rf"{month_pattern}\s+"
        r"(\d{1,2})"
        r"(?:\s+(\d{4}))?\b",
        normalized,
    )

    if month_first_full_match:
        start_month = MONTHS[
            month_first_full_match.group(1)
        ]

        start_day = int(
            month_first_full_match.group(2)
        )

        start_year = (
            int(
                month_first_full_match.group(3)
            )
            if month_first_full_match.group(3)
            else None
        )

        end_month = MONTHS[
            month_first_full_match.group(4)
        ]

        end_day = int(
            month_first_full_match.group(5)
        )

        end_year = (
            int(
                month_first_full_match.group(6)
            )
            if month_first_full_match.group(6)
            else start_year
        )

        start_date = build_month_date(
            day=start_day,
            month=start_month,
            year=start_year,
        )

        if not start_date:
            return None

        end_date = build_month_date(
            day=end_day,
            month=end_month,
            year=(
                end_year
                or start_date.year
            ),
        )

        if not end_date:
            return None

        if end_date < start_date:
            try:
                end_date = end_date.replace(
                    year=end_date.year + 1
                )
            except ValueError:
                return None

        return (
            start_date,
            end_date,
        )


    # ======================================================
    # Month-first, shared month
    #
    # October 9 to 11
    # October 9-11
    # ======================================================

    month_first_shared_match = re.search(
        rf"\b{month_pattern}\s+"
        r"(\d{1,2})"
        r"\s*(?:to|until|through|-)\s*"
        r"(\d{1,2})"
        r"(?:\s+(\d{4}))?\b",
        normalized,
    )

    if month_first_shared_match:
        month = MONTHS[
            month_first_shared_match.group(1)
        ]

        start_day = int(
            month_first_shared_match.group(2)
        )

        end_day = int(
            month_first_shared_match.group(3)
        )

        year = (
            int(
                month_first_shared_match.group(4)
            )
            if month_first_shared_match.group(4)
            else None
        )

        start_date = build_month_date(
            day=start_day,
            month=month,
            year=year,
        )

        if not start_date:
            return None

        end_date = build_month_date(
            day=end_day,
            month=month,
            year=start_date.year,
        )

        if (
            not end_date
            or end_date < start_date
        ):
            return None

        return (
            start_date,
            end_date,
        )


    # ======================================================
    # Day-first, different months
    #
    # 30 August to 2 September
    # ======================================================

    full_range_match = re.search(
        rf"\b(\d{{1,2}})\s+{month_pattern}"
        r"(?:\s+(\d{4}))?"
        r"\s*(?:to|until|through|-)\s*"
        rf"(\d{{1,2}})\s+{month_pattern}"
        r"(?:\s+(\d{4}))?\b",
        normalized,
    )

    if full_range_match:
        start_year = (
            int(
                full_range_match.group(3)
            )
            if full_range_match.group(3)
            else None
        )

        end_year = (
            int(
                full_range_match.group(6)
            )
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

        if not start_date:
            return None

        end_date = build_month_date(
            day=int(
                full_range_match.group(4)
            ),
            month=MONTHS[
                full_range_match.group(5)
            ],
            year=(
                end_year
                or start_date.year
            ),
        )

        if not end_date:
            return None

        if end_date < start_date:
            try:
                end_date = end_date.replace(
                    year=end_date.year + 1
                )
            except ValueError:
                return None

        return (
            start_date,
            end_date,
        )


    # ======================================================
    # Day-first, shared month
    #
    # 3-5 August
    # ======================================================

    shared_month_match = re.search(
        rf"\b(\d{{1,2}})"
        r"\s*(?:to|until|through|-)\s*"
        rf"(\d{{1,2}})\s+{month_pattern}"
        r"(?:\s+(\d{4}))?\b",
        normalized,
    )

    if not shared_month_match:
        return None

    start_day = int(
        shared_month_match.group(1)
    )

    end_day = int(
        shared_month_match.group(2)
    )

    month = MONTHS[
        shared_month_match.group(3)
    ]

    year = (
        int(
            shared_month_match.group(4)
        )
        if shared_month_match.group(4)
        else None
    )

    start_date = build_month_date(
        day=start_day,
        month=month,
        year=year,
    )

    if not start_date:
        return None

    end_date = build_month_date(
        day=end_day,
        month=month,
        year=start_date.year,
    )

    if (
        not end_date
        or end_date < start_date
    ):
        return None

    return (
        start_date,
        end_date,
    )


def parse_date_range(
    text: str,
) -> tuple[date, date] | None:
    """Parse any supported date range."""

    return (
        parse_relative_date_range(text)
        or parse_numbered_date_range(text)
        or parse_weekday_date_range(text)
    )


# ==========================================================
# Recurrence Start Dates
# ==========================================================

def get_recurrence_start_date(
    recurrence: dict | None,
) -> date | None:
    """Return a sensible starting date for recurrence."""

    if not recurrence:
        return None

    today = sg_now().date()
    frequency = recurrence.get("freq")
    byday = recurrence.get("byday", "")

    if frequency == "DAILY":
        return today

    if (
        frequency == "WEEKLY"
        and byday == "MO,TU,WE,TH,FR"
    ):
        start_date = today

        while start_date.weekday() > 4:
            start_date += timedelta(days=1)

        return start_date

    if (
        frequency == "WEEKLY"
        and byday == "SA,SU"
    ):
        days_until_saturday = (
            5 - today.weekday()
        ) % 7

        return (
            today
            + timedelta(
                days=days_until_saturday,
            )
        )

    if (
        frequency == "MONTHLY"
        and recurrence.get("bymonthday")
    ):
        target_day = int(
            recurrence["bymonthday"]
        )

        year = today.year
        month = today.month

        try:
            candidate = date(
                year,
                month,
                target_day,
            )
        except ValueError:
            candidate = None

        if (
            candidate is not None
            and candidate >= today
        ):
            return candidate

        if month == 12:
            year += 1
            month = 1
        else:
            month += 1

        try:
            return date(
                year,
                month,
                target_day,
            )
        except ValueError:
            return None

    return None


# ==========================================================
# Title Cleaning
# ==========================================================

def smart_title_case(
    text: str,
) -> str:
    """Apply readable title casing."""

    words = text.split()

    if not words:
        return "Untitled Event"

    result = []

    for index, word in enumerate(words):
        lowered = word.casefold()

        if lowered in ACRONYMS:
            result.append(
                ACRONYMS[lowered]
            )

        elif (
            index > 0
            and lowered in SMALL_TITLE_WORDS
        ):
            result.append(
                lowered
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
    """Remove parsed date, time, and recurrence phrases."""

    title = normalize_calendar_text(
        text
    )

    patterns = (
        # Recurrence
        r"\bevery\s+weekday\b",
        r"\bevery\s+weekend\b",
        r"\bevery\s+day\b",
        r"\bdaily\b",
        (
            r"\bevery\s+"
            r"(?:monday|tuesday|wednesday|thursday|"
            r"friday|saturday|sunday)\b"
        ),
        (
            r"\bevery\s+month"
            r"(?:\s+on)?"
            r"(?:\s+the)?"
            r"\s+\d{1,2}\b"
        ),
        r"\bevery\s+month\b",
        r"\bmonthly\b",
        r"\bevery\s+year\b",
        r"\byearly\b",

        # Relative ranges
        r"\b(?:this|next)\s+weekend\b",
        r"\bnext\s+week\b",

        # Weekday ranges
        (
            r"\b(?:next\s+)?"
            r"(?:monday|tuesday|wednesday|thursday|"
            r"friday|saturday|sunday)"
            r"\s*(?:to|until|through|-)\s*"
            r"(?:next\s+)?"
            r"(?:monday|tuesday|wednesday|thursday|"
            r"friday|saturday|sunday)\b"
        ),
                # Month-first full ranges
        (
            r"\b"
            r"(?:january|february|march|april|may|"
            r"june|july|august|september|october|"
            r"november|december)"
            r"\s+\d{1,2}"
            r"(?:\s+\d{4})?"
            r"\s*(?:to|until|through|-)\s*"
            r"(?:january|february|march|april|may|"
            r"june|july|august|september|october|"
            r"november|december)"
            r"\s+\d{1,2}"
            r"(?:\s+\d{4})?\b"
        ),

        # Month-first shared-month ranges
        (
            r"\b"
            r"(?:january|february|march|april|may|"
            r"june|july|august|september|october|"
            r"november|december)"
            r"\s+\d{1,2}"
            r"\s*(?:to|until|through|-)\s*"
            r"\d{1,2}"
            r"(?:\s+\d{4})?\b"
        ),

        # Full month ranges
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

        # Shared month ranges
        (
            r"\b\d{1,2}"
            r"\s*(?:to|until|through|-)\s*"
            r"\d{1,2}\s+"
            r"(?:january|february|march|april|may|"
            r"june|july|august|september|october|"
            r"november|december)"
            r"(?:\s+\d{4})?\b"
        ),

        # Relative single dates
        r"\b(?:today|tomorrow)\b",

        # Weekdays
        (
            r"\bnext\s+"
            r"(?:monday|tuesday|wednesday|thursday|"
            r"friday|saturday|sunday)\b"
        ),
        (
            r"\b(?:monday|tuesday|wednesday|thursday|"
            r"friday|saturday|sunday)\b"
        ),

        # Month dates
        (
            r"\b\d{1,2}\s+"
            r"(?:january|february|march|april|may|"
            r"june|july|august|september|october|"
            r"november|december)"
            r"(?:\s+\d{4})?\b"
        ),

        # Times
        (
            r"\b(?:at\s+)?"
            r"\d{1,4}(?:[:.]\d{2})?"
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

    return smart_title_case(
        title
    )


# ==========================================================
# Event Parsing
# ==========================================================

def looks_like_all_day_event(
    text: str,
) -> bool:
    """Return whether the text implies an all-day event."""

    normalized = normalize_calendar_text(
        text
    )

    return any(
        keyword in normalized
        for keyword in ALL_DAY_KEYWORDS
    )


def parse_calendar_event(
    text: str,
) -> dict | None:
    """
    Parse a timed, all-day, multi-day, or recurring event.
    """

    normalized = normalize_calendar_text(
        text
    )

    recurrence = parse_recurrence(
        normalized
    )

    explicit_date = parse_calendar_date(
        normalized
    )

    if (
        recurrence
        and recurrence.get("needs_start_date")
        and explicit_date is None
    ):
        return {
            "incomplete": True,
            "reason": "monthly_day_missing",
            "recurrence": recurrence,
        }

    title = clean_calendar_title(
        normalized
    )

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
            "recurrence": recurrence,
        }

    event_date = explicit_date

    if event_date is None:
        event_date = get_recurrence_start_date(
            recurrence
        )

    event_time = parse_calendar_time(
        normalized
    )

    if (
        event_date is not None
        and event_time is not None
    ):
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
            "recurrence": recurrence,
        }

    if (
        event_date is not None
        and event_time is None
        and (
            looks_like_all_day_event(
                normalized
            )
            or recurrence is not None
        )
    ):
        return {
            "title": title,
            "all_day": True,
            "start_date": event_date,
            "end_date": event_date,
            "recurrence": recurrence,
        }

    return None