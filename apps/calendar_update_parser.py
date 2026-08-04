"""
ShaunMariaOS

Calendar Update Parser
Parses natural-language requests to edit existing events.
"""

import re

from apps.calendar_parser import (
    clean_calendar_title,
    normalize_calendar_text,
    parse_calendar_date,
    parse_calendar_time,
    parse_date_range,
    smart_title_case,
)


UPDATE_VERBS = (
    "move",
    "change",
    "reschedule",
)


def parse_calendar_update(
    text: str,
) -> dict | None:
    """
    Parse a Calendar update request.

    Examples:
        Move dinner to Friday
        Move dinner to Friday 8pm
        Change meeting to 3pm
        Move JB trip to 15-18 Oct
        Rename dinner to Anniversary Dinner
    """

    normalized = normalize_calendar_text(
        text
    )

    rename_match = re.fullmatch(
        r"rename\s+(.+?)\s+to\s+(.+)",
        normalized,
        re.IGNORECASE,
    )

    if rename_match:
        search_text = rename_match.group(1).strip()
        new_title = rename_match.group(2).strip()

        if not search_text or not new_title:
            return None

        return {
            "action": "rename",
            "search_text": smart_title_case(
                search_text
            ),
            "new_title": smart_title_case(
                new_title
            ),
        }

    verb_pattern = "|".join(
        UPDATE_VERBS
    )

    move_match = re.fullmatch(
        rf"(?:{verb_pattern})\s+"
        r"(.+?)\s+to\s+(.+)",
        normalized,
        re.IGNORECASE,
    )

    if not move_match:
        return None

    search_text = move_match.group(1).strip()
    change_text = move_match.group(2).strip()

    if not search_text or not change_text:
        return None

    date_range = parse_date_range(
        change_text
    )

    new_date = parse_calendar_date(
        change_text
    )

    new_time = parse_calendar_time(
        change_text
    )

    if (
        date_range is None
        and new_date is None
        and new_time is None
    ):
        return None

    parsed = {
        "action": "move",
        "search_text": smart_title_case(
            search_text
        ),
        "new_date": new_date,
        "new_time": new_time,
        "new_start_date": None,
        "new_end_date": None,
    }

    if date_range:
        parsed["new_start_date"] = (
            date_range[0]
        )
        parsed["new_end_date"] = (
            date_range[1]
        )

    return parsed