"""
ShaunMariaOS

Calendar Recurrence Parser
"""

import re


WEEKDAY_MAP = {
    "monday": "MO",
    "mon": "MO",
    "tuesday": "TU",
    "tue": "TU",
    "tues": "TU",
    "wednesday": "WE",
    "wed": "WE",
    "thursday": "TH",
    "thu": "TH",
    "thur": "TH",
    "thurs": "TH",
    "friday": "FR",
    "fri": "FR",
    "saturday": "SA",
    "sat": "SA",
    "sunday": "SU",
    "sun": "SU",
}


def parse_recurrence(
    text: str,
) -> dict | None:
    """
    Parse a natural-language recurrence rule.

    Supported examples:
        Every day
        Daily
        Every weekday
        Every weekend
        Every Monday
        Every month on the 1st
        Monthly
        Every year
        Yearly
    """

    normalized = text.strip().casefold()

    # =====================================================
    # Monthly recurrence with an explicit day
    # =====================================================

    monthly_day_match = re.search(
        r"\bevery\s+month"
        r"(?:\s+on)?"
        r"(?:\s+the)?"
        r"\s+(\d{1,2})"
        r"(?:st|nd|rd|th)?\b",
        normalized,
    )

    if monthly_day_match:
        month_day = int(
            monthly_day_match.group(1)
        )

        if not 1 <= month_day <= 31:
            return None

        return {
            "freq": "MONTHLY",
            "bymonthday": month_day,
            "label": (
                f"Every month on the "
                f"{ordinal(month_day)}"
            ),
            "rrule": (
                "RRULE:FREQ=MONTHLY;"
                f"BYMONTHDAY={month_day}"
            ),
        }

    # =====================================================
    # Daily recurrence
    # =====================================================

    if (
        re.search(
            r"\bevery\s+day\b",
            normalized,
        )
        or re.search(
            r"\bdaily\b",
            normalized,
        )
    ):
        return {
            "freq": "DAILY",
            "label": "Every day",
            "rrule": "RRULE:FREQ=DAILY",
        }

    # =====================================================
    # Weekday recurrence
    # =====================================================

    if re.search(
        r"\bevery\s+weekday\b",
        normalized,
    ):
        return {
            "freq": "WEEKLY",
            "byday": "MO,TU,WE,TH,FR",
            "label": "Every weekday",
            "rrule": (
                "RRULE:FREQ=WEEKLY;"
                "BYDAY=MO,TU,WE,TH,FR"
            ),
        }

    # =====================================================
    # Weekend recurrence
    # =====================================================

    if re.search(
        r"\bevery\s+weekend\b",
        normalized,
    ):
        return {
            "freq": "WEEKLY",
            "byday": "SA,SU",
            "label": "Every weekend",
            "rrule": (
                "RRULE:FREQ=WEEKLY;"
                "BYDAY=SA,SU"
            ),
        }

    # =====================================================
    # Weekly recurrence
    # =====================================================

    for weekday, code in WEEKDAY_MAP.items():
        if re.search(
            rf"\bevery\s+{re.escape(weekday)}\b",
            normalized,
        ):
            return {
                "freq": "WEEKLY",
                "byday": code,
                "label": (
                    f"Every "
                    f"{canonical_weekday_name(code)}"
                ),
                "rrule": (
                    "RRULE:FREQ=WEEKLY;"
                    f"BYDAY={code}"
                ),
            }

    # =====================================================
    # Monthly recurrence without a selected day
    # =====================================================

    if (
        re.search(
            r"\bevery\s+month\b",
            normalized,
        )
        or re.search(
            r"\bmonthly\b",
            normalized,
        )
    ):
        return {
            "freq": "MONTHLY",
            "label": "Every month",
            "rrule": "RRULE:FREQ=MONTHLY",
            "needs_start_date": True,
        }

    # =====================================================
    # Yearly recurrence
    # =====================================================

    if (
        re.search(
            r"\bevery\s+year\b",
            normalized,
        )
        or re.search(
            r"\byearly\b",
            normalized,
        )
    ):
        return {
            "freq": "YEARLY",
            "label": "Every year",
            "rrule": "RRULE:FREQ=YEARLY",
        }

    return None


def canonical_weekday_name(
    code: str,
) -> str:
    """Return the full weekday name for an RRULE code."""

    names = {
        "MO": "Monday",
        "TU": "Tuesday",
        "WE": "Wednesday",
        "TH": "Thursday",
        "FR": "Friday",
        "SA": "Saturday",
        "SU": "Sunday",
    }

    return names.get(
        code,
        code,
    )


def ordinal(
    number: int,
) -> str:
    """Return an ordinal number such as 1st or 21st."""

    if 10 <= number % 100 <= 20:
        suffix = "th"
    else:
        suffix = {
            1: "st",
            2: "nd",
            3: "rd",
        }.get(
            number % 10,
            "th",
        )

    return f"{number}{suffix}"