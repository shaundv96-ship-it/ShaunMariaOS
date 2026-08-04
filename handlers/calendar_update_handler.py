"""
ShaunMariaOS

Calendar Update Handler
"""

import re
from datetime import date, datetime, timedelta
from html import escape

from telegram import Update

from apps.calendar_engine import (
    get_calendar_series_master,
    get_event_date_label,
    is_recurring_calendar_event,
    search_calendar_series,
    update_calendar_series,
)
from apps.calendar_update_parser import parse_calendar_update
from apps.menu_keyboard import get_persistent_main_keyboard
from utils.logger import logger
from utils.time import SINGAPORE_TZ


WEEKDAY_RRULE_CODES = {
    0: "MO",
    1: "TU",
    2: "WE",
    3: "TH",
    4: "FR",
    5: "SA",
    6: "SU",
}


def parse_google_datetime(
    value: str,
) -> datetime:
    """Parse a Google Calendar datetime into Singapore time."""

    return datetime.fromisoformat(
        value.replace(
            "Z",
            "+00:00",
        )
    ).astimezone(
        SINGAPORE_TZ
    )


def build_timed_update(
    event: dict,
    parsed_update: dict,
) -> dict:
    """Build start and end changes for a timed event."""

    current_start = parse_google_datetime(
        event["start"]["dateTime"]
    )

    current_end = parse_google_datetime(
        event["end"]["dateTime"]
    )

    duration = (
        current_end
        - current_start
    )

    requested_date = (
        parsed_update.get("new_date")
        or current_start.date()
    )

    requested_time = (
        parsed_update.get("new_time")
        or current_start.time()
    )

    new_start = datetime.combine(
        requested_date,
        requested_time,
        tzinfo=SINGAPORE_TZ,
    )

    new_end = (
        new_start
        + duration
    )

    return {
        "start": {
            "dateTime": new_start.isoformat(),
            "timeZone": "Asia/Singapore",
        },
        "end": {
            "dateTime": new_end.isoformat(),
            "timeZone": "Asia/Singapore",
        },
    }


def build_all_day_update(
    event: dict,
    parsed_update: dict,
) -> dict:
    """
    Build date changes for an all-day event.

    Google Calendar stores the end date exclusively.
    """

    current_start = date.fromisoformat(
        event["start"]["date"]
    )

    current_exclusive_end = date.fromisoformat(
        event["end"]["date"]
    )

    current_inclusive_end = (
        current_exclusive_end
        - timedelta(days=1)
    )

    current_span = (
        current_inclusive_end
        - current_start
    )

    requested_start = parsed_update.get(
        "new_start_date"
    )

    requested_end = parsed_update.get(
        "new_end_date"
    )

    if requested_start and requested_end:
        new_start = requested_start
        new_inclusive_end = requested_end

    else:
        new_start = (
            parsed_update.get("new_date")
            or current_start
        )

        new_inclusive_end = (
            new_start
            + current_span
        )

    return {
        "start": {
            "date": new_start.isoformat(),
        },
        "end": {
            "date": (
                new_inclusive_end
                + timedelta(days=1)
            ).isoformat(),
        },
    }


def update_weekly_recurrence_day(
    event: dict,
    new_date,
) -> list[str] | None:
    """
    Update BYDAY for a simple weekly recurring event.

    Complex rules such as every weekday or every weekend
    are intentionally left unchanged.
    """

    recurrence_rules = event.get(
        "recurrence",
        [],
    )

    if len(recurrence_rules) != 1:
        return None

    original_rule = recurrence_rules[0]

    if "FREQ=WEEKLY" not in original_rule:
        return None

    byday_match = re.search(
        r"BYDAY=([^;]+)",
        original_rule,
    )

    if not byday_match:
        return None

    current_days = byday_match.group(1).split(
        ","
    )

    if len(current_days) != 1:
        return None

    new_code = WEEKDAY_RRULE_CODES[
        new_date.weekday()
    ]

    updated_rule = re.sub(
        r"BYDAY=[^;]+",
        f"BYDAY={new_code}",
        original_rule,
    )

    return [
        updated_rule,
    ]


async def handle_calendar_update(
    update: Update,
    text: str,
) -> None:
    """Find and safely update one Calendar event or series."""

    if not update.message:
        return

    parsed_update = parse_calendar_update(
        text
    )

    if parsed_update is None:
        await update.message.reply_text(
            (
                "⚠️ <b>Calendar Event Not Updated</b>\n\n"
                "Try:\n"
                "<code>Move dinner to Friday 8pm</code>\n"
                "<code>Change meeting to 3pm</code>\n"
                "<code>Rename dinner to Anniversary Dinner</code>"
            ),
            parse_mode="HTML",
            reply_markup=get_persistent_main_keyboard(),
        )
        return

    try:
        search_text = parsed_update[
            "search_text"
        ]

        events = search_calendar_series(
            search_text
        )

        if not events:
            await update.message.reply_text(
                (
                    "🔎 <b>Event Not Found</b>\n\n"
                    "I couldn't find an upcoming event matching "
                    f"<b>{escape(search_text)}</b>."
                ),
                parse_mode="HTML",
                reply_markup=get_persistent_main_keyboard(),
            )
            return

        if len(events) > 1:
            lines = [
                "⚠️ <b>More Than One Event Found</b>",
                "",
                "Nothing was changed. I found:",
            ]

            for event in events[:5]:
                title = escape(
                    event.get(
                        "summary",
                        "Untitled Event",
                    )
                )

                date_label = escape(
                    get_event_date_label(
                        event
                    )
                )

                recurrence_label = (
                    " — Recurring"
                    if is_recurring_calendar_event(event)
                    else ""
                )

                lines.append(
                    f"\n• <b>{title}</b>"
                    f"\n  {date_label}"
                    f"{recurrence_label}"
                )

            lines.extend(
                [
                    "",
                    "Please use a more specific title.",
                ]
            )

            await update.message.reply_text(
                "\n".join(lines),
                parse_mode="HTML",
                reply_markup=get_persistent_main_keyboard(),
            )
            return

        event = events[0]

        is_recurring = is_recurring_calendar_event(
            event
        )

        target_event = (
            get_calendar_series_master(event)
            if is_recurring
            else event
        )

        updates = {}

        if parsed_update["action"] == "rename":
            updates["summary"] = parsed_update[
                "new_title"
            ]

        else:
            is_all_day = (
                "date"
                in target_event.get(
                    "start",
                    {},
                )
            )

            if is_all_day:
                if parsed_update.get(
                    "new_time"
                ):
                    await update.message.reply_text(
                        (
                            "⚠️ <b>Event Not Updated</b>\n\n"
                            "This is currently an all-day event. "
                            "Changing it into a timed event is not "
                            "supported yet."
                        ),
                        parse_mode="HTML",
                        reply_markup=get_persistent_main_keyboard(),
                    )
                    return

                updates.update(
                    build_all_day_update(
                        target_event,
                        parsed_update,
                    )
                )

            else:
                if parsed_update.get(
                    "new_start_date"
                ):
                    await update.message.reply_text(
                        (
                            "⚠️ <b>Event Not Updated</b>\n\n"
                            "A multi-day range cannot currently "
                            "be applied to a timed event."
                        ),
                        parse_mode="HTML",
                        reply_markup=get_persistent_main_keyboard(),
                    )
                    return

                updates.update(
                    build_timed_update(
                        target_event,
                        parsed_update,
                    )
                )

            if (
                is_recurring
                and parsed_update.get("new_date")
            ):
                updated_recurrence = (
                    update_weekly_recurrence_day(
                        target_event,
                        parsed_update["new_date"],
                    )
                )

                if updated_recurrence:
                    updates["recurrence"] = (
                        updated_recurrence
                    )

        updated_event = update_calendar_series(
            event,
            updates,
        )

        updated_title = updated_event.get(
            "summary",
            "Untitled Event",
        )

        updated_date = get_event_date_label(
            updated_event
        )

        heading = (
            "🔁 <b>Recurring Event Series Updated</b>"
            if is_recurring
            else "✏️ <b>Calendar Event Updated</b>"
        )

        message = (
            f"{heading}\n\n"
            f"📌 <b>{escape(updated_title)}</b>\n"
            f"📅 {escape(updated_date)}"
        )

        if is_recurring:
            message += (
                "\n🔁 All future occurrences were updated."
            )

        calendar_link = updated_event.get(
            "htmlLink"
        )

        if calendar_link:
            message += (
                "\n\n"
                f'<a href="{escape(calendar_link, quote=True)}">'
                "🔗 Open in Google Calendar"
                "</a>"
            )

        await update.message.reply_text(
            message,
            parse_mode="HTML",
            disable_web_page_preview=True,
            reply_markup=get_persistent_main_keyboard(),
        )

    except Exception:
        logger.exception(
            "Failed to update Calendar event."
        )

        await update.message.reply_text(
            (
                "❌ <b>Calendar Event Not Updated</b>\n\n"
                "Something went wrong while updating Google Calendar."
            ),
            parse_mode="HTML",
            reply_markup=get_persistent_main_keyboard(),
        )